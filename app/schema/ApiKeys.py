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
    model_config = ConfigDict(from_attributes=True)

    provider: ProviderTypeEnumType
    key_name: str
    key_value: str

    api_base_url: Optional[str]
    api_version: Optional[str]

    is_active: Optional[bool]


class ApiKeyUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: Optional[ProviderTypeEnumType]
    key_name: Optional[str]
    key_value: Optional[str]

    api_base_url: Optional[str]
    api_version: Optional[str]

    is_active: Optional[bool]


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    userId: UUID
    provider: ProviderTypeEnumType
    key_name: str
    key_value: str
    api_base_url: Optional[str]
    api_version: Optional[str]
    last_used_at: Optional[datetime]
    total_requests: int
    is_active: Optional[bool]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
