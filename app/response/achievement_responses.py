from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict


class AchievementCreateResponse(BaseModel):
    """Response for achievement creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Achievement unique identifier")
    title: str = Field(..., description="Achievement title")
    achievement_type: str = Field(..., description="Type of achievement")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Achievement creation timestamp")


class AchievementGetResponse(BaseModel):
    """Response for getting achievement details"""

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


class AchievementUpdateResponse(BaseModel):
    """Response for updating achievement"""

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
    updated_at: datetime = Field(..., description="Last update timestamp")


class AchievementListResponse(BaseModel):
    """Response for listing achievements"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Achievement unique identifier")
    title: str = Field(..., description="Achievement title")
    achievement_type: str = Field(..., description="Type of achievement")
    location: Optional[str] = Field(
        None, description="Location where achievement was earned"
    )
    start_year: Optional[int] = Field(None, description="Start year")
    end_year: Optional[int] = Field(None, description="End year")
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(..., description="Achievement creation timestamp")
