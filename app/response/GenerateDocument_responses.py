from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class GenerateDocCreateResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    userId: UUID
    jobId: UUID
    resume_text: str
    user_response: str
    created_at: datetime


class GeneratedDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    resume_text: str
    userId: str
    jobId: str
    user_response: str
    created_at: datetime
    updated_at: datetime


class DeleteDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    success: bool
    message: str
