from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class CreateGeneratedDocumnet(BaseModel):

    resume_text: str = Field(..., min_length=100)
    userId: str = Field(None)
    jobId: str = Field(None)

    model_config = ConfigDict(from_attributes=True)
