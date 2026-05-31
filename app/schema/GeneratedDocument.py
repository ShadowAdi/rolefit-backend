from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class GeneratedDocumentEnumType(str, Enum):
    RESUME = "Resume"
    COVER_LETTER = "Cover-letter"


class GeneratedDocumentStatusEnumType(str, Enum):
    Pending = "pending"
    Processing = "processing"
    Completed = "completed"
    failed = "failed"


class CreateGeneratedDocumnet(BaseModel):

    resume_text: Optional[str] = None
    cover_letter_text: Optional[str] = None
    userId: Optional[str] = Field(None)
    jobId: Optional[str] = Field(None)
    user_specifications: Optional[str] = Field(None, max_length=1000)
    gen_doc_type: Optional[GeneratedDocumentEnumType] = None
    status: Optional[GeneratedDocumentStatusEnumType] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumentResponseSchema(BaseModel):
    id: str
    userId: str
    jobId: str
    resume_text: Optional[str] = None
    cover_letter_text: Optional[str] = None
    gen_doc_type: str
    user_specifications: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""

    success: bool = Field(..., description="Whether the request was successful")
    status_code: int = Field(200, description="HTTP status code")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc),
        description="Response timestamp",
    )

    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumentApiResponse(ApiResponse[GeneratedDocumentResponseSchema]):
    """API response wrapper for generated document"""

    pass


class GeneratedDocumentListApiResponse(ApiResponse[list]):
    """API response wrapper for list of generated documents"""

    pass


class DeleteDocumentApiResponse(ApiResponse[dict]):
    """API response wrapper for delete document"""

    pass


class DocumentStatusApiResponse(ApiResponse[dict]):
    """API response wrapper for document status"""

    pass
