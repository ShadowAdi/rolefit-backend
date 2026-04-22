from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, List


class ProjectCreateResponse(BaseModel):
    """Response for project creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Project unique identifier")
    title: str = Field(..., description="Project title")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Project creation timestamp")


class ProjectGetResponse(BaseModel):
    """Response for getting project details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Project unique identifier")
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    profileId: UUID = Field(..., description="Associated profile ID")
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    links: Optional[Dict[str, str]] = Field(None, description="Project links")
    startDate: Optional[datetime] = Field(None, description="Project start date")
    endDate: Optional[datetime] = Field(None, description="Project end date")
    priority: Optional[int] = Field(None, description="Priority level")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProjectUpdateResponse(BaseModel):
    """Response for updating project"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Project unique identifier")
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    links: Optional[Dict[str, str]] = Field(None, description="Project links")
    startDate: Optional[datetime] = Field(None, description="Project start date")
    endDate: Optional[datetime] = Field(None, description="Project end date")
    priority: Optional[int] = Field(None, description="Priority level")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProjectListResponse(BaseModel):
    """Response for listing projects"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Project unique identifier")
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    profileId: UUID = Field(..., description="Associated profile ID")
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    startDate: Optional[datetime] = Field(None, description="Project start date")
    endDate: Optional[datetime] = Field(None, description="Project end date")
    priority: Optional[int] = Field(None, description="Priority level")
    created_at: datetime = Field(..., description="Project creation timestamp")
