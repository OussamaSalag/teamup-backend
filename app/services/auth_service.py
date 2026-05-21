from __future__ import annotations

import random
import string
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    enforce_email_domain,
    hash_password,
    verify_password,
)
from app.models.user import User, UserPreference, UserRole
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

# ---------------------------------------------------------------------------
# In-memory verification code store
# TODO: Replace with Redis once REDIS_URL is configured.
#       Key pattern for email verification: email
#       Key pattern for password reset:     "reset_{email}"
# ---------------------------------------------------------------------------
_verification_codes: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_code() -> str:
    """Return a random 6-digit string."""
    return "".join(random.choices(string.digits, k=6))


async def _get_user_role(db: AsyncSession, user_id: UUID) -> str:
    """Return the first role string for a given user, defaulting to 'student'."""
    result = await db.execute(
        select(UserRole).where(UserRole.user_id == user_id)
    )
    role_row = result.scalar_one_or_none()
    return role_row.role if role_row else "student"


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------


class AuthService:

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------

    @staticmethod
    async def register(db: AsyncSession, data: RegisterRequest) -> TokenResponse:
        # 1. Domain check
        enforce_email_domain(data.email)

        # 2. Uniqueness checks
        existing_email = await db.execute(
            select(User).where(User.email == data.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        existing_username = await db.execute(
            select(User).where(User.username == data.username)
        )
        if existing_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        # 3. Create User
        user = User(
            full_name=data.full_name,
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_email_verified=True,
        )
        db.add(user)
        await db.flush()  # populate user.id before FK inserts

        # 4. Create default role
        db.add(UserRole(user_id=user.id, role="student"))

        # 5. Create default preferences
        db.add(UserPreference(user_id=user.id))

        await db.commit()

        # 6. Issue token
        role = "student"
        token = create_access_token({"sub": str(user.id), "role": role})

        return TokenResponse(
            access_token=token,
            user_id=str(user.id),
            role=role,
            full_name=user.full_name,
        )

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    @staticmethod
    async def login(db: AsyncSession, data: LoginRequest) -> TokenResponse:
        _invalid = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # 1. Find user — same error for missing user and wrong password
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if user is None:
            raise _invalid

        # 2. Verify password
        if not verify_password(data.password, user.hashed_password):
            raise _invalid

        # 3. Email verification gate
        if not user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first",
            )

        # 4. Get role & issue token
        role = await _get_user_role(db, user.id)
        token = create_access_token({"sub": str(user.id), "role": role})

        return TokenResponse(
            access_token=token,
            user_id=str(user.id),
            role=role,
            full_name=user.full_name,
        )

    # ------------------------------------------------------------------
    # Password reset — request
    # ------------------------------------------------------------------

    @staticmethod
    async def request_password_reset(
        db: AsyncSession, email: str
    ) -> dict[str, str]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        # Silently ignore unknown emails — don't leak user existence
        if user is not None:
            code = _generate_code()
            _verification_codes[f"reset_{email}"] = code
            print(f"[TeamUp] Password reset code for {email}: {code}")

        return {"message": "If this email exists, a reset code was sent"}

    # ------------------------------------------------------------------
    # Password reset — confirm
    # ------------------------------------------------------------------

    @staticmethod
    async def confirm_password_reset(
        db: AsyncSession, email: str, code: str, new_password: str
    ) -> dict[str, str]:
        store_key = f"reset_{email}"
        stored = _verification_codes.get(store_key)

        if stored is None or stored != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code",
            )

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.hashed_password = hash_password(new_password)
        await db.commit()

        _verification_codes.pop(store_key, None)

        return {"message": "Password reset successful"}


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

auth_service = AuthService()
