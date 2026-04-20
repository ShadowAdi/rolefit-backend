from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class ToolCreateRequest(BaseModel):
    """Request schema for creating a tool"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Tool name")


class ToolUpdateRequest(BaseModel):
    """Request schema for updating a tool"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Tool name")


class ToolResponse(BaseModel):
    """Response schema for tool data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    created_by: UUID = Field(..., description="User ID who created this tool")
    created_at: datetime = Field(..., description="Tool creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
