from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.schemas.task import (
    DashboardResponse,
    ProjectResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)


class TaskService:

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _assert_project_member(
        db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Raise 403 if the user is not a member of the project."""
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project",
            )

    @staticmethod
    async def _get_task_or_404(db: AsyncSession, task_id: uuid.UUID) -> Task:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    @staticmethod
    def _apply_completed_at(task: Task, new_status: str) -> None:
        """Set or clear completed_at based on status transition."""
        if new_status == "done" and task.completed_at is None:
            task.completed_at = datetime.utcnow()
        elif new_status != "done":
            task.completed_at = None

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @staticmethod
    async def create_task(
        db: AsyncSession,
        creator_id: uuid.UUID,
        data: TaskCreate,
    ) -> Task:
        if data.project_id is not None:
            await TaskService._assert_project_member(db, data.project_id, creator_id)

        task = Task(
            title=data.title,
            description=data.description,
            project_id=data.project_id,
            assignee_id=data.assignee_id,
            created_by=creator_id,
            status=data.status,
            source=data.source,
            category=data.category,
            due_date=data.due_date,
            completed_at=datetime.utcnow() if data.status == "done" else None,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @staticmethod
    async def get_my_tasks(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[Task]:
        result = await db.execute(
            select(Task)
            .where(
                or_(Task.assignee_id == user_id, Task.created_by == user_id)
            )
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_project_tasks(
        db: AsyncSession,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Task]:
        await TaskService._assert_project_member(db, project_id, user_id)
        result = await db.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        data: TaskUpdate,
    ) -> Task:
        task = await TaskService._get_task_or_404(db, task_id)

        if task.created_by != user_id and task.assignee_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this task",
            )

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        if "status" in update_data:
            TaskService._apply_completed_at(task, update_data["status"])

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_task_status(
        db: AsyncSession,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        new_status: str,
    ) -> Task:
        task = await TaskService._get_task_or_404(db, task_id)

        if task.created_by != user_id and task.assignee_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task",
            )

        task.status = new_status
        TaskService._apply_completed_at(task, new_status)

        await db.commit()
        await db.refresh(task)
        return task

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        task = await TaskService._get_task_or_404(db, task_id)

        if task.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task creator can delete it",
            )

        await db.delete(task)
        await db.commit()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    @staticmethod
    async def get_dashboard(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> DashboardResponse:
        # 1. Projects where user is a member (latest 5)
        proj_result = await db.execute(
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.created_at.desc())
            .limit(5)
        )
        my_projects = list(proj_result.scalars().all())

        # 2. Tasks summary (status counts for tasks owned/assigned to user)
        task_counts_result = await db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .where(
                or_(Task.assignee_id == user_id, Task.created_by == user_id)
            )
            .group_by(Task.status)
        )
        raw_counts: dict[str, int] = {row.status: row.cnt for row in task_counts_result}
        tasks_summary = {
            "todo": raw_counts.get("todo", 0),
            "in_progress": raw_counts.get("in_progress", 0),
            "done": raw_counts.get("done", 0),
        }

        # 3. Recent tasks (last 5)
        recent_result = await db.execute(
            select(Task)
            .where(
                or_(Task.assignee_id == user_id, Task.created_by == user_id)
            )
            .order_by(Task.created_at.desc())
            .limit(5)
        )
        recent_tasks = list(recent_result.scalars().all())

        # 4. Total members across user's projects (deduplicated)
        member_project_ids = [p.id for p in my_projects]
        total_members = 0
        if member_project_ids:
            count_result = await db.execute(
                select(func.count(ProjectMember.user_id)).where(
                    ProjectMember.project_id.in_(member_project_ids)
                )
            )
            total_members = count_result.scalar_one() or 0

        return DashboardResponse(
            my_projects=[ProjectResponse.model_validate(p) for p in my_projects],
            tasks_summary=tasks_summary,
            recent_tasks=[TaskResponse.model_validate(t) for t in recent_tasks],
            total_members_across_projects=total_members,
        )


task_service = TaskService()
