from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class ToolCreateResponse(BaseModel):
    """Response for tool creation"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    created_by: UUID = Field(..., description="User ID who created this tool")
    created_at: datetime = Field(..., description="Tool creation timestamp")


class ToolGetResponse(BaseModel):
    """Response for getting tool details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    created_by: UUID = Field(..., description="User ID who created this tool")
    created_at: datetime = Field(..., description="Tool creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ToolUpdateResponse(BaseModel):
    """Response for updating tool"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ToolListResponse(BaseModel):
    """Response for listing tools"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Tool unique identifier")
    name: str = Field(..., description="Tool name")
    created_by: UUID = Field(..., description="User ID who created this tool")
    created_at: datetime = Field(..., description="Tool creation timestamp")
