# SiteSense Project Context

## 1. Purpose of this document

This document is the authoritative context for continuing SiteSense
development. It corrects an earlier implementation mistake: the current
repository was initially built as an AI website-idea analysis tool, but the
intended product is a **project tracker**.

Future implementation should follow this document instead of treating the
existing analysis workflow as the product definition.

## 2. Product definition

SiteSense is a lightweight project-tracking application with an AI assistant.
It helps a user create a project, break the project into tasks, track task
status and progress, and use Gemma for practical project planning support.

The central user action is:

> Create and manage a project from a dashboard.

Gemma is an assistant inside the tracker. It is not the primary product and
must not replace normal project-management features.

## 3. What went wrong

There are two related development contexts that became mixed:

1. The original workspace contained the planned full-stack structure under
   `frontend/` and `backend/`.
2. The separately initialized Git repository under `backend/` was pushed to
   GitHub and later expanded to include a copied frontend for Render.

During the rushed MVP work, the product was interpreted as an AI tool that
analyzes a submitted website idea. That produced:

- `POST /analyses`
- `GET /analyses`
- an `Analysis` database model
- a frontend titled “Gemma analysis demo”
- findings and recommendations generated from free-form text

Those features are not the intended core experience. They should be treated as
superseded prototype work. Do not extend the analysis-first UX unless a future
requirement explicitly brings it back.

The phrase “foreign project” refers to project-tracking requirements and
implementation context that were not present in the working repository when
the initial code was generated. The intended tracker behavior must now be
implemented deliberately in this repository.

## 4. Correct MVP scope

The time-boxed MVP should prioritize a complete, demonstrable happy path over
advanced collaboration features.

### Required

- Create a project
- View projects on a dashboard
- View a project's tasks
- Create a task inside a project
- Update task status
- Show basic progress
- Store projects and tasks
- Use Gemma for one useful project-planning action
- Deploy a working demo without paid infrastructure

### Defer

- Multi-user collaboration
- Invitations and roles
- Real-time updates
- Notifications
- File uploads
- Calendar integrations
- Complex reporting
- Billing
- Production-grade authentication
- Hosted durable database

If authentication is needed for presentation, use a simple local/demo user
boundary rather than allowing authentication work to block the tracker flow.

## 5. Suggested user flow

1. User opens the SiteSense dashboard.
2. User creates a project with:
   - name
   - description
   - optional target date
3. The new project appears in the project list.
4. User opens the project workspace.
5. User creates tasks with:
   - title
   - description
   - status
   - priority
   - optional due date
6. User changes task status from Todo to In Progress or Done.
7. Dashboard progress updates from task completion.
8. User asks Gemma to suggest an initial task breakdown or next steps.
9. User accepts useful suggestions by adding them as tasks.

## 6. Core data model

The existing `User` model can remain as a future boundary, but project tracking
should be represented by these models.

### Project

- `id`
- `name`
- `description`
- `status` (`active`, `completed`, or `archived`)
- `target_date` (optional)
- `created_at`
- `updated_at`

### Task

- `id`
- `project_id`
- `title`
- `description` (optional)
- `status` (`todo`, `in_progress`, or `done`)
- `priority` (`low`, `medium`, or `high`)
- `due_date` (optional)
- `created_at`
- `updated_at`

### Optional Project Assistant record

Do not add this until task creation works. If AI history is needed later:

- `id`
- `project_id`
- `prompt`
- `response`
- `created_at`

For the free demo, SQLite is acceptable. The database is local to the running
instance and is not durable on free ephemeral hosting.

## 7. Recommended API

Replace the analysis-first routes with project and task routes.

### Projects

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `PATCH /api/projects/{project_id}`
- `DELETE /api/projects/{project_id}` (or archive instead)

### Tasks

- `GET /api/projects/{project_id}/tasks`
- `POST /api/projects/{project_id}/tasks`
- `PATCH /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`

### AI assistant

- `POST /api/projects/{project_id}/suggest-tasks`

The AI endpoint should receive the project name, description, and current tasks.
It should return structured task suggestions, for example:

```json
{
  "suggestions": [
    {
      "title": "Define the MVP user flow",
      "description": "Write the shortest path from project creation to completion.",
      "priority": "high"
    }
  ]
}
```

The backend must validate the response before presenting suggestions. The AI
must not silently create tasks without user confirmation.

## 8. Frontend screens

The current placeholder page names can be repurposed:

- `Dashboard.tsx`
  - project cards
  - progress indicators
  - create-project action
- `Analysis.tsx`
  - rename or replace with `Project.tsx` / `ProjectWorkspace.tsx`
  - task list
  - task creation form
  - status controls
  - “Suggest tasks with Gemma” action
- `History.tsx`
  - replace with project archive or activity view
- `Login.tsx`
  - keep as a deferred placeholder unless authentication is explicitly needed

The main UI should use project-tracking language. Remove or rewrite labels such
as “Analyze with Gemma”, “findings”, and “recommendations” from the primary
workflow.

## 9. AI integration

Gemma should support the tracker rather than define it.

Good MVP AI use:

- Generate an initial task breakdown from a project description
- Suggest the next task based on incomplete work
- Identify risks or missing planning steps

The AI response should be structured into task suggestions or concise planning
advice. Keep the API key on the backend in `GEMINI_API_KEY`; never expose it to
the React client.

The configured model is controlled by:

```env
GEMMA_MODEL=gemma-4-26b-a4b-it
```

The exact model identifier must be confirmed against the models available to
the Google AI Studio key before the final demo.

## 10. Repository and deployment context

The actively pushed repository is:

<https://github.com/kabakadev/sitesenseAI>

Its current branch is `main`. The backend repository now contains a copied
frontend and a Dockerfile that builds the React app and serves it from
FastAPI.

The intended low-cost hosting path is one Render Web Service:

- Runtime: Docker
- Branch: `main`
- Health check: `/health`
- Environment variables:
  - `GEMINI_API_KEY`
  - `GEMMA_MODEL`

Render's free filesystem is ephemeral. SQLite data can be lost when the
service restarts, sleeps, or redeploys. This is acceptable for a presentation
MVP, but it must be disclosed as a limitation. A durable PostgreSQL database
can be added later if hosting or payment constraints change.

## 11. Migration plan from the wrong implementation

Implement the pivot in this order:

1. Add `Project` and `Task` SQLAlchemy models.
2. Add Pydantic schemas for project and task creation/update/response.
3. Add project and task service functions.
4. Add project and task API routes under `/api`.
5. Replace the analysis form with a dashboard and project workspace.
6. Add the Gemma “suggest tasks” endpoint.
7. Add task-suggestion display and user-confirmed task creation.
8. Remove or mark `/analyses` as legacy.
9. Update the README and deployment instructions.
10. Build and manually verify the complete create-project-to-complete-task
    flow.

The first implementation of this corrected slice now provides the project and
task routes, computed progress, and the Gemma task-suggestion endpoint. The
remaining future work is the broader construction operations surface, not the
core tracker happy path.

Do not spend the remaining project time on a full authentication system,
database migration framework, or multi-user permissions unless the core tracker
flow is already working.

## 12. Definition of done for the corrected MVP

The corrected MVP is complete when a reviewer can:

1. Open the deployed SiteSense URL.
2. Create a project.
3. Add at least two tasks.
4. Change one task to In Progress and another to Done.
5. See the project progress change.
6. Request Gemma task suggestions.
7. Add a suggested task after reviewing it.
8. Refresh the page and see the stored data while the free instance remains
   alive.

The application should clearly present itself as a project tracker with an AI
assistant, not as a website-idea analysis tool.
