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
    headline: Optional[str] = Field(None, description="Professional headline")
    resume_link: Optional[str] = Field(None, description="Link to user's resume")
    cover_letter_link: Optional[str] = Field(
        None, description="Link to user's cover letter"
    )
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    links: Optional[Dict[str, Any]] = Field(None, description="Social profile links")
    isOnboarded: bool = Field(
        False, description="Whether the user has finished the onboarding wizard"
    )
    created_at: datetime = Field(..., description="Profile creation timestamp")


class ProfileGetResponse(BaseModel):
    """Response for getting profile details"""

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
    isOnboarded: bool = Field(
        False, description="Whether the user has finished the onboarding wizard"
    )
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")


class ProfileUpdateResponse(BaseModel):
    """Response for updating user profile"""

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
    isOnboarded: bool = Field(
        False, description="Whether the user has finished the onboarding wizard"
    )
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
    headline: Optional[str] = Field(None, description="Professional headline")
    resume_link: Optional[str] = Field(None, description="Link to user's resume")
    cover_letter_link: Optional[str] = Field(
        None, description="Link to user's cover letter"
    )
    isOnboarded: bool = Field(
        False, description="Whether the user has finished the onboarding wizard"
    )
    created_at: datetime = Field(..., description="Profile creation timestamp")


class ProfileOnboardingResponse(BaseModel):
    """Response for marking onboarding complete"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Profile unique identifier")
    userId: UUID = Field(..., description="Associated user ID")
    isOnboarded: bool = Field(..., description="Onboarding completion flag")
    updated_at: datetime = Field(..., description="Last profile update timestamp")
