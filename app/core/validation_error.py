"""
Custom validation error response for better frontend error handling
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ValidationErrorField(BaseModel):
    """Individual field validation error"""

    field: str
    code: str
    message: str
    constraint: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Structured validation error response"""

    status: str = "validation_error"
    message: str
    errors: List[ValidationErrorField]


class ValidationHelper:
    """Helper class to create structured validation errors"""

    @staticmethod
    def create_field_error(
        field: str, code: str, message: str, constraint: Optional[str] = None
    ) -> ValidationErrorField:
        """Create a structured field error"""
        return ValidationErrorField(
            field=field, code=code, message=message, constraint=constraint
        )

    @staticmethod
    def create_response(
        message: str, errors: List[ValidationErrorField]
    ) -> ValidationErrorResponse:
        """Create a structured validation error response"""
        return ValidationErrorResponse(message=message, errors=errors)
