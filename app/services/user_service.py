from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ProfileSkill, Skill, User
from app.schemas.project import SkillResponse
from app.schemas.user import (
    UserProfileResponse,
    UserPublicResponse,
    UserUpdateRequest,
)


class UserService:

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _get_user_or_404(db: AsyncSession, user_id: uuid.UUID) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    async def _get_user_skills(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[Skill]:
        result = await db.execute(
            select(Skill)
            .join(ProfileSkill, ProfileSkill.skill_id == Skill.id)
            .where(ProfileSkill.profile_id == user_id)
            .order_by(Skill.category, Skill.name)
        )
        return list(result.scalars().all())

    @staticmethod
    def _build_profile(user: User, skills: list[Skill]) -> UserProfileResponse:
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            cover_url=user.cover_url,
            bio=user.bio,
            grade=user.grade,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            skills=[SkillResponse.model_validate(s) for s in skills],
        )

    # ------------------------------------------------------------------
    # Get profile
    # ------------------------------------------------------------------

    @staticmethod
    async def get_profile(
        db: AsyncSession, user_id: uuid.UUID
    ) -> UserProfileResponse:
        user = await UserService._get_user_or_404(db, user_id)
        skills = await UserService._get_user_skills(db, user_id)
        return UserService._build_profile(user, skills)

    # ------------------------------------------------------------------
    # Update profile
    # ------------------------------------------------------------------

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: uuid.UUID,
        data: UserUpdateRequest,
    ) -> UserProfileResponse:
        user = await UserService._get_user_or_404(db, user_id)

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        skills = await UserService._get_user_skills(db, user_id)
        return UserService._build_profile(user, skills)

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    @staticmethod
    async def get_my_skills(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[SkillResponse]:
        skills = await UserService._get_user_skills(db, user_id)
        return [SkillResponse.model_validate(s) for s in skills]

    @staticmethod
    async def add_skill(
        db: AsyncSession,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
    ) -> list[SkillResponse]:
        # 1. Skill must exist
        skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
        if skill_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found",
            )

        # 2. Check for duplicate
        dup_result = await db.execute(
            select(ProfileSkill).where(
                ProfileSkill.profile_id == user_id,
                ProfileSkill.skill_id == skill_id,
            )
        )
        if dup_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Skill already added to your profile",
            )

        db.add(ProfileSkill(profile_id=user_id, skill_id=skill_id))
        await db.commit()

        return await UserService.get_my_skills(db, user_id)

    @staticmethod
    async def remove_skill(
        db: AsyncSession,
        user_id: uuid.UUID,
        skill_id: uuid.UUID,
    ) -> list[SkillResponse]:
        # 1. Count current skills
        count_result = await db.execute(
            select(ProfileSkill).where(ProfileSkill.profile_id == user_id)
        )
        current_skills = list(count_result.scalars().all())

        if len(current_skills) <= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot have fewer than 10 skills",
            )

        # 2. Find and delete the specific ProfileSkill row
        row_result = await db.execute(
            select(ProfileSkill).where(
                ProfileSkill.profile_id == user_id,
                ProfileSkill.skill_id == skill_id,
            )
        )
        row = row_result.scalar_one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found on your profile",
            )

        await db.delete(row)
        await db.commit()

        return await UserService.get_my_skills(db, user_id)

    # ------------------------------------------------------------------
    # Search users
    # ------------------------------------------------------------------

    @staticmethod
    async def search_users(
        db: AsyncSession, query: str
    ) -> list[UserPublicResponse]:
        pattern = f"%{query}%"
        result = await db.execute(
            select(User)
            .where(
                or_(
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
            .limit(20)
        )
        users = result.scalars().all()
        return [UserPublicResponse.model_validate(u) for u in users]

    # ------------------------------------------------------------------
    # All skills (catalogue)
    # ------------------------------------------------------------------

    @staticmethod
    async def get_all_skills(db: AsyncSession) -> list[SkillResponse]:
        result = await db.execute(
            select(Skill).order_by(Skill.category, Skill.name)
        )
        return [SkillResponse.model_validate(s) for s in result.scalars().all()]


user_service = UserService()
