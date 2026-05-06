import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.services.notification_service import notification_service

from app.models.project import (
    Project,
    ProjectJoinRequest,
    ProjectMember,
    ProjectSkill,
    ProjectStatusEnum,
)
from app.models.user import Skill, User
from app.schemas.project import (
    JoinRequestResponse,
    MemberResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    SkillResponse,
)


class ProjectService:
    @staticmethod
    async def _format_project(project: Project) -> ProjectResponse:
        members = []
        for pm in project.members:
            user = pm.user
            members.append(
                MemberResponse(
                    user_id=pm.user_id,
                    full_name=user.full_name,
                    username=user.username,
                    avatar_url=user.avatar_url,
                    role=pm.role,
                    joined_at=pm.joined_at,
                )
            )

        skills = []
        for ps in project.skills:
            skill = ps.skill
            skills.append(
                SkillResponse(
                    id=skill.id,
                    name=skill.name,
                    category=skill.category or "",
                )
            )

        return ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description or "",
            cover_url=project.cover_url,
            owner_id=project.owner_id,
            status=project.status,
            max_members=project.max_members,
            created_at=project.created_at,
            updated_at=project.updated_at,
            member_count=len(members),
            members=members,
            required_skills=skills,
        )

    @classmethod
    async def create_project(
        cls, db: AsyncSession, user_id: uuid.UUID, data: ProjectCreate
    ) -> ProjectResponse:
        project = Project(
            title=data.title,
            description=data.description,
            max_members=data.max_members,
            owner_id=user_id,
            status="open",
        )
        db.add(project)
        await db.flush()

        owner_member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role="owner",
        )
        db.add(owner_member)

        for skill_id in data.required_skill_ids:
            ps = ProjectSkill(project_id=project.id, skill_id=skill_id)
            db.add(ps)

        await db.commit()

        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.skills).selectinload(ProjectSkill.skill),
            )
            .where(Project.id == project.id)
        )
        result = await db.execute(stmt)
        project_obj = result.scalar_one()

        return await cls._format_project(project_obj)

    @classmethod
    async def get_project(cls, db: AsyncSession, project_id: uuid.UUID) -> ProjectResponse:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.skills).selectinload(ProjectSkill.skill),
            )
            .where(Project.id == project_id)
        )
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return await cls._format_project(project)

    @classmethod
    async def list_projects(
        cls, db: AsyncSession, status: Optional[str], page: int, limit: int
    ) -> List[ProjectResponse]:
        stmt = select(Project).options(
            selectinload(Project.members).selectinload(ProjectMember.user),
            selectinload(Project.skills).selectinload(ProjectSkill.skill),
        )
        if status:
            stmt = stmt.where(Project.status == status)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await db.execute(stmt)
        projects = result.scalars().all()

        return [await cls._format_project(p) for p in projects]

    @classmethod
    async def update_project(
        cls, db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID, data: ProjectUpdate
    ) -> ProjectResponse:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.skills).selectinload(ProjectSkill.skill),
            )
            .where(Project.id == project_id)
        )
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update project")

        if data.title is not None:
            project.title = data.title
        if data.description is not None:
            project.description = data.description
        if data.max_members is not None:
            project.max_members = data.max_members

        if data.required_skill_ids is not None:
            await db.execute(
                delete(ProjectSkill).where(ProjectSkill.project_id == project_id)
            )

            for skill_id in data.required_skill_ids:
                ps = ProjectSkill(project_id=project.id, skill_id=skill_id)
                db.add(ps)

        await db.commit()
        return await cls.get_project(db, project_id)

    @classmethod
    async def delete_project(cls, db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID):
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete project")

        await db.delete(project)
        await db.commit()

    @classmethod
    async def request_join(
        cls, db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID, message: Optional[str]
    ) -> JoinRequestResponse:
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        member_stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        member_res = await db.execute(member_stmt)
        if member_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already a member")

        req_stmt = select(ProjectJoinRequest).where(
            ProjectJoinRequest.project_id == project_id,
            ProjectJoinRequest.user_id == user_id,
            ProjectJoinRequest.status == "pending",
        )
        req_res = await db.execute(req_stmt)
        if req_res.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Pending request already exists")

        join_request = ProjectJoinRequest(
            project_id=project_id,
            user_id=user_id,
            message=message,
            status="pending",
        )
        db.add(join_request)
        await db.commit()

        # Notify project owner of new join request
        await notification_service.create_notification(
            db,
            user_id=project.owner_id,
            type="join_request",
            payload={
                "project_id": str(project_id),
                "requester_id": str(user_id),
            },
        )

        user_stmt = select(User).where(User.id == user_id)
        user = (await db.execute(user_stmt)).scalar_one()

        return JoinRequestResponse(
            id=join_request.id,
            project_id=join_request.project_id,
            user_id=join_request.user_id,
            username=user.username,
            full_name=user.full_name,
            message=join_request.message,
            status=join_request.status,
            created_at=join_request.created_at,
        )

    @classmethod
    async def list_join_requests(
        cls, db: AsyncSession, project_id: uuid.UUID, owner_id: uuid.UUID
    ) -> List[JoinRequestResponse]:
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        req_stmt = (
            select(ProjectJoinRequest, User)
            .join(User, ProjectJoinRequest.user_id == User.id)
            .where(ProjectJoinRequest.project_id == project_id)
        )
        req_res = await db.execute(req_stmt)

        results = []
        for req, user in req_res.all():
            results.append(
                JoinRequestResponse(
                    id=req.id,
                    project_id=req.project_id,
                    user_id=req.user_id,
                    username=user.username,
                    full_name=user.full_name,
                    message=req.message,
                    status=req.status,
                    created_at=req.created_at,
                )
            )
        return results

    @classmethod
    async def respond_to_request(
        cls, db: AsyncSession, request_id: uuid.UUID, owner_id: uuid.UUID, status: str
    ) -> JoinRequestResponse:
        req_stmt = select(ProjectJoinRequest).where(ProjectJoinRequest.id == request_id)
        req_res = await db.execute(req_stmt)
        join_request = req_res.scalar_one_or_none()

        if not join_request:
            raise HTTPException(status_code=404, detail="Request not found")

        proj_stmt = select(Project).where(Project.id == join_request.project_id)
        proj_res = await db.execute(proj_stmt)
        project = proj_res.scalar_one()

        if project.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if join_request.status != "pending":
            raise HTTPException(status_code=400, detail="Request is not pending")

        join_request.status = status
        join_request.responded_at = datetime.utcnow()

        if status == "accepted":
            new_member = ProjectMember(
                project_id=project.id,
                user_id=join_request.user_id,
                role="member",
            )
            db.add(new_member)

        await db.commit()

        # Notify requester of the decision
        if status == "accepted":
            await notification_service.create_notification(
                db,
                user_id=join_request.user_id,
                type="request_accepted",
                payload={
                    "project_id": str(project.id),
                    "project_title": project.title,
                },
            )

        user_stmt = select(User).where(User.id == join_request.user_id)
        user = (await db.execute(user_stmt)).scalar_one()

        return JoinRequestResponse(
            id=join_request.id,
            project_id=join_request.project_id,
            user_id=join_request.user_id,
            username=user.username,
            full_name=user.full_name,
            message=join_request.message,
            status=join_request.status,
            created_at=join_request.created_at,
        )

    @classmethod
    async def get_my_teams(cls, db: AsyncSession, user_id: uuid.UUID) -> List[ProjectResponse]:
        stmt = (
            select(Project)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.skills).selectinload(ProjectSkill.skill),
            )
            .where(ProjectMember.user_id == user_id)
        )
        result = await db.execute(stmt)
        projects = result.scalars().all()

        return [await cls._format_project(p) for p in projects]

    @classmethod
    async def search_projects(cls, db: AsyncSession, query: str) -> List[ProjectResponse]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.skills).selectinload(ProjectSkill.skill),
            )
            .where(
                or_(
                    Project.title.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                )
            )
        )
        result = await db.execute(stmt)
        projects = result.scalars().all()

        return [await cls._format_project(p) for p in projects]
