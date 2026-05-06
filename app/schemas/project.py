from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class SkillResponse(BaseModel):
    id: UUID
    name: str
    category: str
    
    model_config = ConfigDict(from_attributes=True)

class MemberResponse(BaseModel):
    user_id: UUID
    full_name: str
    username: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    title: str
    description: str
    max_members: int = 5
    required_skill_ids: List[UUID] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_members: Optional[int] = None
    required_skill_ids: Optional[List[UUID]] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str
    cover_url: Optional[str] = None
    owner_id: UUID
    status: str
    max_members: int
    created_at: datetime
    updated_at: datetime
    member_count: int = 0
    members: List[MemberResponse] = Field(default_factory=list)
    required_skills: List[SkillResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class JoinRequestCreate(BaseModel):
    message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class JoinRequestResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    username: str
    full_name: str
    message: Optional[str] = None
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RespondToRequest(BaseModel):
    status: str
    
    model_config = ConfigDict(from_attributes=True)
