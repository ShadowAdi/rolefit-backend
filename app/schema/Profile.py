from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class ProfileCreateRequest(BaseModel):
    """Request schema for creating a profile"""

    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(
        ..., min_length=1, max_length=255, description="User full name"
    )
    headline: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Professional headline"
    )
    summary: Optional[str] = Field(
        None, max_length=2000, description="Professional summary or bio"
    )
    resume_link: Optional[str] = Field(None, description="Link to user's resume")
    cover_letter_link: Optional[str] = Field(
        None, description="Link to user's cover letter"
    )
    links: Optional[Dict[str, Any]] = Field(
        None, description="Links to social profiles or portfolios"
    )


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating a profile"""

    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="User full name"
    )
    headline: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Professional headline"
    )
    summary: Optional[str] = Field(
        None, max_length=2000, description="Professional summary or bio"
    )
    resume_link: Optional[str] = Field(None, description="Link to user's resume")
    cover_letter_link: Optional[str] = Field(
        None, description="Link to user's cover letter"
    )
    links: Optional[Dict[str, Any]] = Field(
        None, description="Links to social profiles or portfolios"
    )


class ProfileResponse(BaseModel):
    """Response schema for profile data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    full_name: str = Field(..., description="User full name")
    headline: Optional[str] = Field(None, description="Professional headline")
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    resume_link: Optional[str] = Field(None, description="Link to user's resume")
    cover_letter_link: Optional[str] = Field(
        None, description="Link to user's cover letter"
    )
    links: Optional[Dict[str, Any]] = Field(None, description="Social profile links")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")
