from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ToolCreateRequest(BaseModel):
    """Request schema for creating a tool"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Tool name")


class ToolUpdateRequest(BaseModel):
    """Request schema for updating a tool"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255, description="Tool name")


class AddToolToUserRequest(BaseModel):
    """Request schema for adding a tool to user profile.

    Accept EITHER toolId OR toolName:
    - toolId: Add existing tool directly
    - toolName: Create tool if doesn't exist, then add (all in one call)
    """

    model_config = ConfigDict(from_attributes=True)

    toolId: Optional[UUID] = Field(None, description="Tool ID (if tool already exists)")
    toolName: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Tool name (create if not exists, then add)",
    )


class ToolResponse(BaseModel):
    """Response schema for tool data"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    created_by: UUID = Field(..., description="User ID who created this tool")
    created_at: datetime = Field(..., description="Tool creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
