from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List


class ExperienceCreateRequest(BaseModel):
    """Request schema for creating an experience"""

    model_config = ConfigDict(from_attributes=True)

    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Company name"
    )
    description: str = Field(
        ..., min_length=1, max_length=2000, description="Experience description"
    )
    role: str = Field(
        ..., min_length=1, max_length=255, description="Job role or position"
    )
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    employment_type: Optional[str] = Field(
        None, description="Employment type (e.g., Full-time, Part-time, Contract)"
    )
    location_type: Optional[str] = Field(
        None, description="Location type (e.g., On-site, Remote, Hybrid)"
    )
    location_details: Optional[str] = Field(
        None, max_length=255, description="Specific location details"
    )
    start_month: Optional[int] = Field(
        None, ge=1, le=12, description="Start month (1-12)"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12)")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")


class ExperienceUpdateRequest(BaseModel):
    """Request schema for updating an experience"""

    model_config = ConfigDict(from_attributes=True)

    company_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Company name"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=2000, description="Experience description"
    )
    role: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Job role or position"
    )
    techStack: Optional[List[str]] = Field(
        None, description="Technologies and tools used"
    )
    employment_type: Optional[str] = Field(
        None, description="Employment type (e.g., Full-time, Part-time, Contract)"
    )
    location_type: Optional[str] = Field(
        None, description="Location type (e.g., On-site, Remote, Hybrid)"
    )
    location_details: Optional[str] = Field(
        None, max_length=255, description="Specific location details"
    )
    start_month: Optional[int] = Field(
        None, ge=1, le=12, description="Start month (1-12)"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12)")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")


class ExperienceResponse(BaseModel):
    """Response schema for experience data"""

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
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Experience creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
