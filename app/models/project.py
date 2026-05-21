from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

ProjectStatusEnum = Enum(
    "draft", "open", "in_progress", "completed", "archived",
    name="project_status_enum",
)

MemberRoleEnum = Enum("owner", "member", name="member_role_enum")

JoinRequestStatusEnum = Enum(
    "pending", "accepted", "rejected", name="join_request_status_enum"
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        ProjectStatusEnum, nullable=False, default="open"
    )
    max_members: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
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
    members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )
    skills: Mapped[list[ProjectSkill]] = relationship(
        "ProjectSkill", back_populates="project", cascade="all, delete-orphan"
    )
    join_requests: Mapped[list[ProjectJoinRequest]] = relationship(
        "ProjectJoinRequest", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", name="pk_project_members"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(MemberRoleEnum, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="project_memberships")
class ProjectSkill(Base):
    __tablename__ = "project_skills"
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "skill_id", name="pk_project_skills"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="project_skills")


class ProjectJoinRequest(Base):
    __tablename__ = "project_join_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        JoinRequestStatusEnum, nullable=False, default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="join_requests")
