from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.project import SkillResponse


# ---------------------------------------------------------------------------
# Public profile (search results, viewing other users)
# ---------------------------------------------------------------------------

class UserPublicResponse(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    grade: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Update request
# ---------------------------------------------------------------------------

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    grade: Optional[int] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Skill add request
# ---------------------------------------------------------------------------

class SkillAddRequest(BaseModel):
    skill_id: uuid.UUID


# ---------------------------------------------------------------------------
# Full private profile (own profile / authenticated view)
# ---------------------------------------------------------------------------

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    bio: Optional[str] = None
    grade: Optional[int] = None
    is_email_verified: bool
    created_at: datetime
    skills: list[SkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
