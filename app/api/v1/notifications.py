from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import MarkReadRequest, NotificationResponse
from app.services.notification_service import notification_service

router = APIRouter(tags=["Notifications"])


# ---------------------------------------------------------------------------
# GET /  — list my notifications
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    return await notification_service.get_my_notifications(db, current_user.id)


# ---------------------------------------------------------------------------
# GET /unread-count
# ---------------------------------------------------------------------------

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return await notification_service.get_unread_count(db, current_user.id)


# ---------------------------------------------------------------------------
# POST /mark-read
# ---------------------------------------------------------------------------

@router.post("/mark-read")
async def mark_as_read(
    data: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return await notification_service.mark_as_read(
        db, current_user.id, data.notification_ids
    )
