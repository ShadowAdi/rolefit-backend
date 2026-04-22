from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class ProfileCreateResponse(BaseModel):
    """Response for profile creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    full_name: str = Field(..., description="User full name")
    headline: str = Field(..., description="Professional headline")
    resume_link: str = Field(..., description="Link to user's resume")
    cover_letter_link: str = Field(..., description="Link to user's cover letter")
    created_at: datetime = Field(..., description="Profile creation timestamp")


class ProfileGetResponse(BaseModel):
    """Response for getting profile details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    full_name: str = Field(..., description="User full name")
    headline: str = Field(..., description="Professional headline")
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    resume_link: str = Field(..., description="Link to user's resume")
    cover_letter_link: str = Field(..., description="Link to user's cover letter")
    links: Optional[Dict[str, Any]] = Field(None, description="Social profile links")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")


class ProfileUpdateResponse(BaseModel):
    """Response for updating user profile"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    full_name: str = Field(..., description="User full name")
    headline: str = Field(..., description="Professional headline")
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    resume_link: str = Field(..., description="Link to user's resume")
    cover_letter_link: str = Field(..., description="Link to user's cover letter")
    links: Optional[Dict[str, Any]] = Field(None, description="Social profile links")
    updated_at: datetime = Field(..., description="Last profile update timestamp")


class ProfileDeleteResponse(BaseModel):
    """Response for deleting a profile"""

    model_config = ConfigDict(from_attributes=True)

    message: str = Field(..., description="Success message")
    id: UUID = Field(..., description="Deleted profile ID")
    full_name: str = Field(..., description="User full name of deleted profile")


class ProfileListResponse(BaseModel):
    """Response for listing profiles"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    full_name: str = Field(..., description="User full name")
    headline: str = Field(..., description="Professional headline")
    resume_link: str = Field(..., description="Link to user's resume")
    cover_letter_link: str = Field(..., description="Link to user's cover letter")
    created_at: datetime = Field(..., description="Profile creation timestamp")
