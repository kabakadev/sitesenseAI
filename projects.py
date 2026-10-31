from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from models import Project, Task
from schemas import (
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
)


def project_summary(db: Session, project: Project) -> dict:
    task_count, completed_count = db.execute(
        select(
            func.count(Task.id),
            func.sum(case((Task.status == "done", 1), else_=0)),
        ).where(Task.project_id == project.id)
    ).one()
    task_count = int(task_count or 0)
    completed_count = int(completed_count or 0)
    return {
        "task_count": task_count,
        "completed_task_count": completed_count,
        "completion": round(completed_count / task_count * 100) if task_count else 0,
    }


def list_projects(db: Session) -> list[dict]:
    return [
        {**project.__dict__, **project_summary(db, project)}
        for project in db.scalars(select(Project).order_by(Project.created_at.desc())).all()
    ]


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def create_project(db: Session, request: ProjectCreate) -> Project:
    project = Project(**request.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session, project: Project, request: ProjectUpdate
) -> Project:
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def list_tasks(db: Session, project_id: int) -> list[Task]:
    return list(
        db.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        ).all()
    )


def create_task(db: Session, project_id: int, request: TaskCreate) -> Task:
    task = Task(project_id=project_id, **request.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, request: TaskUpdate) -> Task:
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task
