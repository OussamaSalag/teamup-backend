from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.register(db, data)



# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.login(db, data)


# ---------------------------------------------------------------------------
# POST /reset-password/request
# ---------------------------------------------------------------------------


@router.post("/reset-password/request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await auth_service.request_password_reset(db, data.email)


# ---------------------------------------------------------------------------
# POST /reset-password/confirm
# ---------------------------------------------------------------------------


@router.post("/reset-password/confirm")
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await auth_service.confirm_password_reset(
        db, data.email, data.code, data.new_password
    )


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
