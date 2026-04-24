from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List


class CreateGeneratedDocumnet(BaseModel):

    resume_text: str = Field(..., min_length=100)
    userId: str = Field(None)
    jobId: str = Field(None)

    model_config = ConfigDict(from_attributes=True)
