from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    location: str | None = None
    budget: int | None = Field(default=None, ge=0)
    target_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    location: str | None = None
    budget: int | None = Field(default=None, ge=0)
    target_date: date | None = None
    status: str | None = None


class ProjectResponse(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_task_count: int = 0
    completion: int = 0


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str = "todo"
    priority: str = "medium"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: date | None = None


class TaskResponse(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class TaskSuggestion(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"


class TaskSuggestionResponse(BaseModel):
    suggestions: list[TaskSuggestion]
