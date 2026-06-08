# app/schema/Verification.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class EmailVerificationRequest(BaseModel):
    """Request model for email verification"""

    model_config = ConfigDict(from_attributes=True)

    token: str


class EmailVerificationResponse(BaseModel):
    """Response model for email verification"""

    model_config = ConfigDict(from_attributes=True)

    message: str
    is_verified: bool
    verified_at: datetime | None = None


class ResendVerificationRequest(BaseModel):
    """Request model for resending verification email"""

    model_config = ConfigDict(from_attributes=True)

    email: str


class EmailVerificationStatus(BaseModel):
    """Model for email verification status"""

    model_config = ConfigDict(from_attributes=True)

    is_verified: bool
    user_id: UUID
    email: str
