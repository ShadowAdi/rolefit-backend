from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class PublicationCreateResponse(BaseModel):
    """Response for publication creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Publication unique identifier")
    title: str = Field(..., description="Publication title")
    publisher: str = Field(..., description="Publisher name")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(
        ..., description="Publication record creation timestamp"
    )


class PublicationGetResponse(BaseModel):
    """Response for getting publication details"""

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


class PublicationUpdateResponse(BaseModel):
    """Response for updating publication"""

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
    updated_at: datetime = Field(..., description="Last update timestamp")


class PublicationListResponse(BaseModel):
    """Response for listing publications"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Publication unique identifier")
    title: str = Field(..., description="Publication title")
    publisher: str = Field(..., description="Publisher name")
    publication_date: datetime = Field(..., description="Publication date")
    priority: Optional[int] = Field(None, description="Priority level")
    profileId: UUID = Field(..., description="Associated profile ID")
    created_at: datetime = Field(
        ..., description="Publication record creation timestamp"
    )
