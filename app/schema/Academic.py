from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class AcademicCreateRequest(BaseModel):
    """Request schema for creating an academic record"""

    model_config = ConfigDict(from_attributes=True)

    degree_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Degree name (e.g., Bachelor of Science)",
    )
    college_name: str = Field(
        ..., min_length=1, max_length=255, description="College or university name"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Additional details about the degree"
    )
    links: Optional[Dict[str, str]] = Field(
        None,
        description="Links related to academic record (e.g., certificate, transcript)",
    )
    start_month: Optional[int] = Field(
        None, ge=1, le=12, description="Start month (1-12)"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12)")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class AcademicUpdateRequest(BaseModel):
    """Request schema for updating an academic record"""

    model_config = ConfigDict(from_attributes=True)

    degree_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Degree name"
    )
    college_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="College or university name"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Additional details about the degree"
    )
    links: Optional[Dict[str, str]] = Field(
        None, description="Links related to academic record"
    )
    start_month: Optional[int] = Field(
        None, ge=1, le=12, description="Start month (1-12)"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12)")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class AcademicResponse(BaseModel):
    """Response schema for academic data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Academic record unique identifier")
    degree_name: str = Field(..., description="Degree name")
    college_name: str = Field(..., description="College or university name")
    profileId: UUID = Field(..., description="Associated profile ID")
    description: Optional[str] = Field(
        None, description="Additional details about the degree"
    )
    links: Optional[Dict[str, str]] = Field(
        None, description="Links related to academic record"
    )
    start_month: Optional[int] = Field(None, description="Start month")
    start_year: Optional[int] = Field(None, description="Start year")
    end_month: Optional[int] = Field(None, description="End month")
    end_year: Optional[int] = Field(None, description="End year")
    priority: Optional[int] = Field(None, description="Priority level")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
