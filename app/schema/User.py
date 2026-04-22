from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import TypeVar, Generic, Optional, List, Any

T = TypeVar("T")


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=3, description="User password")


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: Optional[EmailStr] = Field(None, description="User email")
    password: Optional[str] = Field(None, min_length=3, description="User password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime


class UserRegisterResponse(BaseModel):
    """Response for user registration"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")


class UserGetResponse(BaseModel):
    """Response for getting user details"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")


class UserAuthenticatedResponse(BaseModel):
    """Response for authenticated user (includes token)"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserUpdateResponse(BaseModel):
    """Response for updating user profile"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    updated_at: datetime = Field(..., description="Last profile update timestamp")


class UserDeleteResponse(BaseModel):
    """Response for user deletion"""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(True, description="Whether deletion was successful")
    message: str = Field(
        "User account deleted successfully", description="Deletion confirmation message"
    )
    deleted_user_id: UUID = Field(..., description="ID of the deleted user")
    deleted_at: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc),
        description="Deletion timestamp",
    )


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)
    success: bool = Field(..., description="Whether the request was successful")
    status_code: int = Field(200, description="HTTP status code")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc),
        description="Response timestamp",
    )


class RegisterApiResponse(ApiResponse[UserRegisterResponse]):
    """API response wrapper for user registration"""

    pass


class GetUserApiResponse(ApiResponse[UserGetResponse]):
    """API response wrapper for get user"""

    pass


class AuthenticatedUserApiResponse(ApiResponse[UserAuthenticatedResponse]):
    """API response wrapper for authenticated user (login/register with token)"""

    pass


class UpdateUserApiResponse(ApiResponse[UserUpdateResponse]):
    """API response wrapper for update user"""

    pass


class DeleteUserApiResponse(ApiResponse[UserDeleteResponse]):
    """API response wrapper for delete user"""

    pass
