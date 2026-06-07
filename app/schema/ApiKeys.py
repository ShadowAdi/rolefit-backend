from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


class ProviderTypeEnumType(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"
    OTHER = "other"


class ApiKeyCreateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    provider: ProviderTypeEnumType
    key_name: str
    key_value: str
    api_base_url: Optional[str] = None  # Make optional with default None
    api_version: Optional[str] = None  # Make optional with default None
    is_active: Optional[bool] = True
    isDefault: Optional[bool] = False  # Keep as isDefault for DB
    expires_at: Optional[datetime] = None  # Make optional with default None


class ApiKeyUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    provider: Optional[ProviderTypeEnumType] = None
    key_name: Optional[str] = None
    key_value: Optional[str] = None
    api_base_url: Optional[str] = None
    api_version: Optional[str] = None
    is_active: Optional[bool] = None
    isDefault: Optional[bool] = None
    expires_at: Optional[datetime] = None


class KeyFetchHelperResponse(BaseModel):
    message: Optional[str]
    success: bool
    api_key: Optional[str]


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID = Field(alias="userId")
    provider: ProviderTypeEnumType
    key_name: str
    key_value: str
    api_base_url: Optional[str] = None
    api_version: Optional[str] = None
    last_used_at: Optional[datetime] = None
    total_requests: int = 0
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    isDefault: Optional[bool] = None
