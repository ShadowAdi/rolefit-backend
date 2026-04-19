from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=3, description="User password")


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime
