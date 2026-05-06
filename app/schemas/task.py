from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

# ---------------------------------------------------------------------------
# Allowed enum values (mirror SQLAlchemy enums without importing SA)
# ---------------------------------------------------------------------------

_TASK_STATUSES = {"todo", "in_progress", "done"}
_TASK_SOURCES = {"project", "mentor", "personal", "system"}
_PROJECT_STATUSES = {"draft", "open", "in_progress", "completed", "archived"}


# ---------------------------------------------------------------------------
# Project sub-schema (used inside DashboardResponse)
# ---------------------------------------------------------------------------


class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    owner_id: uuid.UUID
    status: str
    max_members: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Task request schemas
# ---------------------------------------------------------------------------


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None
    status: str = "todo"
    source: str = "personal"
    category: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in _TASK_STATUSES:
            raise ValueError(f"status must be one of {sorted(_TASK_STATUSES)}")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in _TASK_SOURCES:
            raise ValueError(f"source must be one of {sorted(_TASK_SOURCES)}")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[uuid.UUID] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in _TASK_STATUSES:
            raise ValueError(f"status must be one of {sorted(_TASK_STATUSES)}")
        return v


class TaskStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in _TASK_STATUSES:
            raise ValueError(f"status must be one of {sorted(_TASK_STATUSES)}")
        return v


# ---------------------------------------------------------------------------
# Task response schema
# ---------------------------------------------------------------------------


class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    source: str
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Dashboard response schema
# ---------------------------------------------------------------------------


class DashboardResponse(BaseModel):
    my_projects: list[ProjectResponse]
    tasks_summary: dict[str, int]          # {todo: N, in_progress: N, done: N}
    recent_tasks: list[TaskResponse]       # last 5
    total_members_across_projects: int
