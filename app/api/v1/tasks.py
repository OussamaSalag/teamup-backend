from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.task import (
    DashboardResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import task_service

router = APIRouter(tags=["Tasks"])


# ---------------------------------------------------------------------------
# GET /  — my tasks
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[TaskResponse])
async def get_my_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return await task_service.get_my_tasks(db, current_user.id)


# ---------------------------------------------------------------------------
# POST /  — create task
# ---------------------------------------------------------------------------


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    return await task_service.create_task(db, current_user.id, data)


# ---------------------------------------------------------------------------
# GET /dashboard
# ---------------------------------------------------------------------------


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    return await task_service.get_dashboard(db, current_user.id)


# ---------------------------------------------------------------------------
# GET /project/{project_id}  — project tasks
# ---------------------------------------------------------------------------


@router.get("/project/{project_id}", response_model=list[TaskResponse])
async def get_project_tasks(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return await task_service.get_project_tasks(db, project_id, current_user.id)


# ---------------------------------------------------------------------------
# PUT /{task_id}  — full update
# ---------------------------------------------------------------------------


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    return await task_service.update_task(db, task_id, current_user.id, data)


# ---------------------------------------------------------------------------
# PATCH /{task_id}/status  — status-only update
# ---------------------------------------------------------------------------


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: uuid.UUID,
    data: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> object:
    return await task_service.update_task_status(
        db, task_id, current_user.id, data.status
    )


# ---------------------------------------------------------------------------
# DELETE /{task_id}
# ---------------------------------------------------------------------------


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await task_service.delete_task(db, task_id, current_user.id)
