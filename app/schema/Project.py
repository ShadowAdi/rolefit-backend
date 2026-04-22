from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List


class ProjectCreateRequest(BaseModel):
    """Request schema for creating a project"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: str = Field(
        ..., min_length=1, max_length=2000, description="Project description"
    )
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    links: Optional[Dict[str, str]] = Field(
        None, description="Project links (e.g., github, live demo, portfolio)"
    )
    startDate: Optional[datetime] = Field(None, description="Project start date")
    endDate: Optional[datetime] = Field(None, description="Project end date")
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class ProjectUpdateRequest(BaseModel):
    """Request schema for updating a project"""

    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Project title"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=2000, description="Project description"
    )
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    links: Optional[Dict[str, str]] = Field(
        None, description="Project links (e.g., github, live demo, portfolio)"
    )
    startDate: Optional[datetime] = Field(None, description="Project start date")
    endDate: Optional[datetime] = Field(None, description="Project end date")
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class ProjectResponse(BaseModel):
    """Response schema for project data"""

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
