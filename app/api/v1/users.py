from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project import SkillResponse
from app.schemas.user import (
    SkillAddRequest,
    UserProfileResponse,
    UserPublicResponse,
    UserUpdateRequest,
)
from app.services.user_service import user_service

router = APIRouter(tags=["Users"])


# ---------------------------------------------------------------------------
# GET /me  — own full profile
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    return await user_service.get_profile(db, current_user.id)


# ---------------------------------------------------------------------------
# PUT /me  — update own profile
# ---------------------------------------------------------------------------

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    return await user_service.update_profile(db, current_user.id, data)


# ---------------------------------------------------------------------------
# GET /me/skills
# ---------------------------------------------------------------------------

@router.get("/me/skills", response_model=list[SkillResponse])
async def get_my_skills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SkillResponse]:
    return await user_service.get_my_skills(db, current_user.id)


# ---------------------------------------------------------------------------
# POST /me/skills
# ---------------------------------------------------------------------------

@router.post(
    "/me/skills",
    response_model=list[SkillResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_skill(
    data: SkillAddRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SkillResponse]:
    return await user_service.add_skill(db, current_user.id, data.skill_id)


# ---------------------------------------------------------------------------
# DELETE /me/skills/{skill_id}
# ---------------------------------------------------------------------------

@router.delete("/me/skills/{skill_id}", response_model=list[SkillResponse])
async def remove_skill(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SkillResponse]:
    return await user_service.remove_skill(db, current_user.id, skill_id)


# ---------------------------------------------------------------------------
# GET /skills  — full skill catalogue (public)
# ---------------------------------------------------------------------------

@router.get("/skills", response_model=list[SkillResponse])
async def get_all_skills(
    db: AsyncSession = Depends(get_db),
) -> list[SkillResponse]:
    return await user_service.get_all_skills(db)


# ---------------------------------------------------------------------------
# GET /search?q=
# ---------------------------------------------------------------------------

@router.get("/search", response_model=list[UserPublicResponse])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserPublicResponse]:
    return await user_service.search_users(db, q)


# ---------------------------------------------------------------------------
# GET /{user_id}  — public profile by ID
# ---------------------------------------------------------------------------

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    return await user_service.get_profile(db, user_id)
