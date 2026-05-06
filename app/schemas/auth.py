from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]+$")


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    username: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_min_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v.strip()

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 20:
            raise ValueError("Username must be at most 20 characters")
        if not USERNAME_RE.match(v):
            raise ValueError(
                "Username may only contain letters, numbers, and underscores"
            )
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: str

    @field_validator("code")
    @classmethod
    def code_is_six_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v):
            raise ValueError("Verification code must be exactly 6 digits")
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @field_validator("code")
    @classmethod
    def code_is_six_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v):
            raise ValueError("Reset code must be exactly 6 digits")
        return v

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str


class UserResponse(BaseModel):
    id: uuid.UUID          # UUID object from ORM; FastAPI serialises to string
    email: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    grade: Optional[int] = None
    is_email_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
