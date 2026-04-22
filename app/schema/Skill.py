from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class SkillCreateRequest(BaseModel):
    """Request schema for creating a skill"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Skill name")


class SkillUpdateRequest(BaseModel):
    """Request schema for updating a skill"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Skill name")


class AddSkillToUserRequest(BaseModel):
    """Request schema for adding a skill to user profile.
    
    Accept EITHER skillId OR skillName:
    - skillId: Add existing skill directly
    - skillName: Create skill if doesn't exist, then add (all in one call)
    """

    model_config = ConfigDict(from_attributes=True)

    skillId: Optional[UUID] = Field(None, description="Skill ID (if skill already exists)")
    skillName: Optional[str] = Field(None, min_length=1, max_length=255, description="Skill name (create if not exists, then add)")


class SkillResponse(BaseModel):
    """Response schema for skill data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    created_by: UUID = Field(..., description="User ID who created this skill")
    created_at: datetime = Field(..., description="Skill creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
