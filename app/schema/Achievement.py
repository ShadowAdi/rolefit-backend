from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, List


class AchievementCreateRequest(BaseModel):
    """Request schema for creating an achievement"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ..., min_length=1, max_length=255, description="Achievement title"
    )
    achievement_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of achievement (e.g., Award, Certification, Recognition)",
    )
    description: str = Field(
        ..., min_length=1, max_length=2000, description="Achievement description"
    )
    location: Optional[str] = Field(
        None, max_length=255, description="Location where achievement was earned"
    )
    start_month: Optional[str] = Field(
        None, max_length=20, description="Start month name or abbreviation"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[str] = Field(
        None, max_length=20, description="End month name or abbreviation"
    )
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")
    links: Optional[Dict[str, str]] = Field(
        None, description="Links related to the achievement (e.g., certificate, proof)"
    )
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class AchievementUpdateRequest(BaseModel):
    """Request schema for updating an achievement"""

    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Achievement title"
    )
    achievement_type: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Type of achievement"
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=2000, description="Achievement description"
    )
    location: Optional[str] = Field(
        None, max_length=255, description="Location where achievement was earned"
    )
    start_month: Optional[str] = Field(
        None, max_length=20, description="Start month name or abbreviation"
    )
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_month: Optional[str] = Field(
        None, max_length=20, description="End month name or abbreviation"
    )
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")
    links: Optional[Dict[str, str]] = Field(
        None, description="Links related to the achievement"
    )
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class AchievementResponse(BaseModel):
    """Response schema for achievement data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Achievement unique identifier")
    title: str = Field(..., description="Achievement title")
    achievement_type: str = Field(..., description="Type of achievement")
    description: str = Field(..., description="Achievement description")
    location: Optional[str] = Field(
        None, description="Location where achievement was earned"
    )
    start_month: Optional[str] = Field(None, description="Start month")
    start_year: Optional[int] = Field(None, description="Start year")
    end_month: Optional[str] = Field(None, description="End month")
    end_year: Optional[int] = Field(None, description="End year")
    links: Optional[Dict[str, str]] = Field(
        None, description="Links related to the achievement"
    )
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Achievement creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
