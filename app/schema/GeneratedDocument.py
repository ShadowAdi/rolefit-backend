from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class CreateGeneratedDocumnet(BaseModel):

    resume_text: str = Field(..., min_length=100)
    userId: str = Field(None)
    jobId: str = Field(None)

    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    resume_text: str
    userId: str
    jobId: str
    created_at: datetime
    updated_at: datetime


class DeleteDocumnetResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str
    success: bool
    message: str
