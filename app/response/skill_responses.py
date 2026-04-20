from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class SkillCreateResponse(BaseModel):
    """Response for skill creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    created_by: UUID = Field(..., description="User ID who created this skill")
    created_at: datetime = Field(..., description="Skill creation timestamp")


class SkillGetResponse(BaseModel):
    """Response for getting skill details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    created_by: UUID = Field(..., description="User ID who created this skill")
    created_at: datetime = Field(..., description="Skill creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SkillUpdateResponse(BaseModel):
    """Response for updating skill"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SkillListResponse(BaseModel):
    """Response for listing skills"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Skill unique identifier")
    name: str = Field(..., description="Skill name")
    created_by: UUID = Field(..., description="User ID who created this skill")
    created_at: datetime = Field(..., description="Skill creation timestamp")
