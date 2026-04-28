from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from typing import Optional


class GeneratedDocumentEnumType(str, Enum):
    RESUME = "Resume"
    COVER_LETTER = "Cover-letter"


class CreateGeneratedDocumnet(BaseModel):

    resume_text: Optional[str]
    cover_letter_text: Optional[str]
    userId: str = Field(None)
    jobId: str = Field(None)
    user_specifications = Field(..., max_length=1000)
    gen_doc_type: Optional[GeneratedDocumentEnumType] = None

    model_config = ConfigDict(from_attributes=True)
