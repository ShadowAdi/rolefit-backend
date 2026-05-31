from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


class GeneratedDocumentEnumType(str, Enum):
    RESUME = "Resume"
    COVER_LETTER = "Cover-letter"


class GenerateDocCreateResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    userId: UUID
    jobId: UUID
    resume_text: Optional[str]
    cover_letter_text: Optional[str]
    gen_doc_type: str
    user_specifications: Optional[str]
    created_at: datetime


class GeneratedDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_text: Optional[str]
    cover_letter_text: Optional[str]
    userId: UUID
    jobId: UUID
    gen_doc_type: str
    status: str
    user_specifications: Optional[str]
    created_at: datetime
    updated_at: datetime


class DeleteDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    success: bool
    message: str
