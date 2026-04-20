from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict


class AcademicCreateResponse(BaseModel):
    """Response for academic record creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Academic record unique identifier")
    degree_name: str = Field(..., description="Degree name")
    college_name: str = Field(..., description="College or university name")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Record creation timestamp")


class AcademicGetResponse(BaseModel):
    """Response for getting academic record details"""

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
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AcademicUpdateResponse(BaseModel):
    """Response for updating academic record"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Academic record unique identifier")
    degree_name: str = Field(..., description="Degree name")
    college_name: str = Field(..., description="College or university name")
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
    updated_at: datetime = Field(..., description="Last update timestamp")


class AcademicListResponse(BaseModel):
    """Response for listing academic records"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Academic record unique identifier")
    degree_name: str = Field(..., description="Degree name")
    college_name: str = Field(..., description="College or university name")
    profileId: UUID = Field(..., description="Associated profile ID")
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year")
    created_at: datetime = Field(..., description="Record creation timestamp")
