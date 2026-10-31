# SiteSense Project Tracker

SiteSense is a minimal construction project-tracking application with a
Gemma-powered planning assistant. The React frontend and FastAPI backend are
served together by one Docker web service.

## Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add a free Google AI Studio key to `.env`:

```env
GEMINI_API_KEY=your-key-here
GEMMA_MODEL=gemma-3-27b-it
```

Start the API:

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000`. SQLite is used by default, so PostgreSQL is not
required for the MVP.

## MVP workflow

- Create a construction project.
- Add tasks to the project.
- Move tasks between Todo, In Progress, and Done.
- See completion calculated from completed tasks.
- Ask Gemma for practical task suggestions and add suggestions selectively.

API routes:

```text
GET   /health
GET   /api/v1/projects
POST  /api/v1/projects
GET   /api/v1/projects/{id}
PATCH /api/v1/projects/{id}
GET   /api/v1/projects/{id}/tasks
POST  /api/v1/projects/{id}/tasks
PATCH /api/v1/tasks/{id}
POST  /api/v1/projects/{id}/suggest-tasks
```

## Render deployment

Create a **Web Service** from
<https://github.com/kabakadev/sitesenseAI>.

| Setting | Value |
|---|---|
| Runtime | Docker |
| Branch | `main` |
| Dockerfile | `./Dockerfile` |
| Instance type | Free |
| Health check path | `/health` |

Add these encrypted environment variables in Render:

```text
GEMINI_API_KEY=<Google AI Studio key>
GEMMA_MODEL=gemma-3-27b-it
```

Render supplies `PORT`; the Docker command uses it automatically. The free
filesystem is ephemeral, so SQLite project data can disappear after a restart
or redeploy. That limitation is acceptable for this demonstration MVP.

## Scope note

The interface is based on the contributor construction-intelligence frontend,
but the implemented scope is intentionally limited to projects, tasks,
progress, and Gemma task suggestions. Authentication, team collaboration,
finance, materials, uploads, and computer vision remain future work.
