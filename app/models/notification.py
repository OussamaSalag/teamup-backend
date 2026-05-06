from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

NotificationTypeEnum = Enum(
    "join_request",
    "request_accepted",
    "task_assigned",
    "new_message",
    "mentor_feedback",
    name="notification_type_enum",
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(NotificationTypeEnum, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    user: Mapped[object] = relationship("User")
