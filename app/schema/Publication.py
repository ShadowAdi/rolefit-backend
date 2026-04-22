from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class PublicationCreateRequest(BaseModel):
    """Request schema for creating a publication"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ..., min_length=1, max_length=500, description="Publication title"
    )
    publisher: str = Field(
        ..., min_length=1, max_length=255, description="Publisher name"
    )
    publication_date: datetime = Field(..., description="Publication date")
    authors: List[str] = Field(
        ..., min_items=1, max_items=100, description="List of author names"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Publication description or abstract"
    )
    url: Optional[str] = Field(
        None, max_length=2000, description="URL to the publication"
    )
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class PublicationUpdateRequest(BaseModel):
    """Request schema for updating a publication"""

    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Publication title"
    )
    publisher: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Publisher name"
    )
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    authors: Optional[List[str]] = Field(
        None, min_items=1, max_items=100, description="List of author names"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Publication description or abstract"
    )
    url: Optional[str] = Field(
        None, max_length=2000, description="URL to the publication"
    )
    priority: Optional[int] = Field(
        None, ge=0, description="Priority level (higher number = higher priority)"
    )


class PublicationResponse(BaseModel):
    """Response schema for publication data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Publication unique identifier")
    title: str = Field(..., description="Publication title")
    publisher: str = Field(..., description="Publisher name")
    publication_date: datetime = Field(..., description="Publication date")
    authors: List[str] = Field(..., description="List of author names")
    description: Optional[str] = Field(
        None, description="Publication description or abstract"
    )
    url: Optional[str] = Field(None, description="URL to the publication")
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(
        ..., description="Publication record creation timestamp"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")
