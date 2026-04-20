from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class SkillCreateRequest(BaseModel):
    """Request schema for creating a skill"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Skill name")


class SkillUpdateRequest(BaseModel):
    """Request schema for updating a skill"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Skill name")


class SkillResponse(BaseModel):
    """Response schema for skill data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    created_by: UUID = Field(..., description="User ID who created this skill")
    created_at: datetime = Field(..., description="Skill creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
