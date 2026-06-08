from pydantic import BaseModel, ConfigDict
from typing import TypeVar

T = TypeVar("T")


class ConfirmVerificationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str
