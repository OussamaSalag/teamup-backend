from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationResponse


class NotificationService:

    # ------------------------------------------------------------------
    # Create (called internally by other services)
    # ------------------------------------------------------------------

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: uuid.UUID,
        type: str,
        payload: dict,
    ) -> None:
        notification = Notification(
            user_id=user_id,
            type=type,
            payload=payload,
        )
        db.add(notification)
        await db.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @staticmethod
    async def get_my_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[NotificationResponse]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
        )
        notifications = result.scalars().all()
        return [NotificationResponse.model_validate(n) for n in notifications]

    # ------------------------------------------------------------------
    # Mark as read
    # ------------------------------------------------------------------

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        user_id: uuid.UUID,
        notification_ids: list[uuid.UUID],
    ) -> dict:
        result = await db.execute(
            update(Notification)
            .where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,   # ownership guard
                Notification.read_at.is_(None),    # skip already-read
            )
            .values(read_at=datetime.utcnow())
            .returning(Notification.id)
        )
        updated_ids = result.fetchall()
        await db.commit()
        return {"updated": len(updated_ids)}

    # ------------------------------------------------------------------
    # Unread count
    # ------------------------------------------------------------------

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict:
        result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
        )
        count = result.scalar_one() or 0
        return {"count": count}


notification_service = NotificationService()
