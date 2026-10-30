# SiteSense MVP

SiteSense is a minimal full-stack demo using React, FastAPI, SQLite, and Gemma
through the Google AI Studio Gemini API. The backend serves the built frontend,
so the complete application deploys as one web service.

## Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add a free key from [Google AI Studio](https://aistudio.google.com/apikey) to
`.env`:

```env
GEMINI_API_KEY=your-key-here
GEMMA_MODEL=gemma-3-27b-it
```

Run the API:

```bash
uvicorn main:app --reload
```

For frontend development, use a second terminal:

```bash
cd backend/frontend
npm install
npm run dev
```

The default database is a local `sitesense.db` SQLite file. The API supports:

- `GET /health`
- `POST /analyses`
- `GET /analyses`

## Render deployment

Create a **Web Service** from the `kabakadev/sitesenseAI` repository:

| Setting | Value |
|---|---|
| Environment | Docker |
| Branch | `main` |
| Dockerfile path | `./Dockerfile` |
| Instance type | Free |
| Health check path | `/health` |

Add these environment variables in Render:

```text
GEMINI_API_KEY=<paste your Google AI Studio key in Render>
GEMMA_MODEL=gemma-3-27b-it
```

Render supplies `PORT` automatically. The Docker image uses it and defaults to
`8000` locally. The deployed service serves both the React frontend and API
from the same URL.

The free Render filesystem is ephemeral, so SQLite history can disappear when
the service restarts or redeploys. This is acceptable for the MVP demo. Do not
commit `.env` or API keys.
