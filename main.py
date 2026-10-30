from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from analysis import create_analysis, list_analyses
from database import Base, engine, get_db
from gemma import GemmaConfigurationError, GemmaRequestError
from models import Analysis, User
from schemas import AnalysisCreate, AnalysisResponse, HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="SiteSense API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="sitesense-api")


@app.post(
    "/analyses",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis_endpoint(
    request: AnalysisCreate, db: Session = Depends(get_db)
) -> Analysis:
    try:
        return create_analysis(db, request)
    except GemmaConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except GemmaRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.get("/analyses", response_model=list[AnalysisResponse])
def get_analyses(db: Session = Depends(get_db)) -> list[Analysis]:
    return list_analyses(db)


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    requested_file = static_dir / path
    if path and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(static_dir / "index.html")
