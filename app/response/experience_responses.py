from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ExperienceCreateResponse(BaseModel):
    """Response for experience creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Experience unique identifier")
    company_name: str = Field(..., description="Company name")
    role: str = Field(..., description="Job role or position")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Experience creation timestamp")


class ExperienceGetResponse(BaseModel):
    """Response for getting experience details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Experience unique identifier")
    company_name: str = Field(..., description="Company name")
    description: str = Field(..., description="Experience description")
    role: str = Field(..., description="Job role or position")
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    employment_type: Optional[str] = Field(None, description="Employment type")
    location_type: Optional[str] = Field(None, description="Location type")
    location_details: Optional[str] = Field(
        None, description="Specific location details"
    )
    start_month: Optional[int] = Field(None, description="Start month")
    start_year: Optional[int] = Field(None, description="Start year")
    end_month: Optional[int] = Field(None, description="End month")
    end_year: Optional[int] = Field(None, description="End year")
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Experience creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ExperienceUpdateResponse(BaseModel):
    """Response for updating experience"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Experience unique identifier")
    company_name: str = Field(..., description="Company name")
    description: str = Field(..., description="Experience description")
    role: str = Field(..., description="Job role or position")
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    employment_type: Optional[str] = Field(None, description="Employment type")
    location_type: Optional[str] = Field(None, description="Location type")
    location_details: Optional[str] = Field(
        None, description="Specific location details"
    )
    start_month: Optional[int] = Field(None, description="Start month")
    start_year: Optional[int] = Field(None, description="Start year")
    end_month: Optional[int] = Field(None, description="End month")
    end_year: Optional[int] = Field(None, description="End year")
    priority: Optional[int] = Field(None, description="Priority level")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ExperienceListResponse(BaseModel):
    """Response for listing experiences"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Experience unique identifier")
    company_name: str = Field(..., description="Company name")
    role: str = Field(..., description="Job role or position")
    employment_type: Optional[str] = Field(None, description="Employment type")
    location_type: Optional[str] = Field(None, description="Location type")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year")
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Experience creation timestamp")
