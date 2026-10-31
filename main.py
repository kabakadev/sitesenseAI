from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from gemma import GemmaConfigurationError, GemmaRequestError, suggest_tasks
from models import Project, Task
from projects import (
    create_project,
    create_task,
    get_project,
    list_projects,
    list_tasks,
    update_project,
    update_task,
    project_summary,
)
from schemas import (
    HealthResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskSuggestionResponse,
    TaskUpdate,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="SiteSense Project Tracker API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="sitesense-api")


@app.get("/api/v1/projects", response_model=list[ProjectResponse])
def projects(db: Session = Depends(get_db)) -> list[dict]:
    return list_projects(db)


@app.post("/api/v1/projects", response_model=ProjectResponse, status_code=201)
def add_project(
    request: ProjectCreate, db: Session = Depends(get_db)
) -> dict:
    project = create_project(db, request)
    return {**project.__dict__, **project_summary(db, project)}


@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def project(project_id: int, db: Session = Depends(get_db)) -> dict:
    item = get_project(db, project_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {**item.__dict__, **project_summary(db, item)}


@app.patch("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def edit_project(
    project_id: int, request: ProjectUpdate, db: Session = Depends(get_db)
) -> dict:
    item = get_project(db, project_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Project not found")
    item = update_project(db, item, request)
    return {**item.__dict__, **project_summary(db, item)}


@app.get("/api/v1/projects/{project_id}/tasks", response_model=list[TaskResponse])
def tasks(project_id: int, db: Session = Depends(get_db)) -> list[Task]:
    if get_project(db, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return list_tasks(db, project_id)


@app.post(
    "/api/v1/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_task(
    project_id: int, request: TaskCreate, db: Session = Depends(get_db)
) -> Task:
    if get_project(db, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return create_task(db, project_id, request)


@app.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
def edit_task(
    task_id: int, request: TaskUpdate, db: Session = Depends(get_db)
) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return update_task(db, task, request)


@app.post(
    "/api/v1/projects/{project_id}/suggest-tasks",
    response_model=TaskSuggestionResponse,
)
def suggest_project_tasks(
    project_id: int, db: Session = Depends(get_db)
) -> TaskSuggestionResponse:
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        suggestions = suggest_tasks(
            project.name,
            project.description or "",
            [task.title for task in list_tasks(db, project_id)],
        )
    except GemmaConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except GemmaRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return TaskSuggestionResponse(suggestions=suggestions)


static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    requested_file = static_dir / path
    if path and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(static_dir / "index.html")
