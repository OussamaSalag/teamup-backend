from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

RoleEnum = Enum("student", "mentor", "admin", name="role_enum")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    roles: Mapped[list[UserRole]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[list[ProfileSkill]] = relationship(
        "ProfileSkill", back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional[UserPreference]] = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    project_memberships: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="user", cascade="all, delete-orphan"
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_roles_user_role"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(RoleEnum, nullable=False)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="roles")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    profile_skills: Mapped[list[ProfileSkill]] = relationship(
        "ProfileSkill", back_populates="skill"
    )
    project_skills: Mapped[list["ProjectSkill"]] = relationship(
        "ProjectSkill", back_populates="skill"
    )


class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    __table_args__ = (
        PrimaryKeyConstraint("profile_id", "skill_id", name="pk_profile_skills"),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="profile_skills")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    theme: Mapped[str] = mapped_column(String(20), nullable=False, default="system")
    notification_prefs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="preferences")
