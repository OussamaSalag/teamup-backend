import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project import (
    JoinRequestCreate,
    JoinRequestResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RespondToRequest,
)
from app.services.project_service import ProjectService

router = APIRouter(tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.list_projects(db, status, page, limit)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.create_project(db, current_user.id, data)


@router.get("/search", response_model=List[ProjectResponse])
async def search_projects(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.search_projects(db, q)


@router.get("/my-teams", response_model=List[ProjectResponse])
async def get_my_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.get_my_teams(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.get_project(db, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.update_project(db, project_id, current_user.id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ProjectService.delete_project(db, project_id, current_user.id)


@router.post("/{project_id}/join", response_model=JoinRequestResponse)
async def request_join(
    project_id: uuid.UUID,
    data: JoinRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.request_join(db, project_id, current_user.id, data.message)


@router.get("/{project_id}/requests", response_model=List[JoinRequestResponse])
async def list_join_requests(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.list_join_requests(db, project_id, current_user.id)


@router.post("/{project_id}/requests/{request_id}/respond", response_model=JoinRequestResponse)
async def respond_to_request(
    project_id: uuid.UUID,
    request_id: uuid.UUID,
    data: RespondToRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.respond_to_request(db, request_id, current_user.id, data.status)
