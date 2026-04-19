from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    """Response containing JWT token and user info"""

    token: str
    token_type: str = "bearer"
    sub: str
    email: str
    exp_at: str


class TokenData(BaseModel):
    sub: str
    email: str
    exp_at: str
