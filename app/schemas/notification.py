from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    payload: dict
    read_at: Optional[datetime] = None
    created_at: datetime

    @property
    def title(self) -> str:
        return self.payload.get("title", "Notification")

    @property
    def body(self) -> str:
        return self.payload.get("body", "")

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    model_config = ConfigDict(from_attributes=True)


class MarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID]
