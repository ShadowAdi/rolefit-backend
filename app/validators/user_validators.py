import re
from typing import Optional
from pydantic import ValidationError, field_validator, BaseModel


class UserValidator(BaseModel):
    """Validators for User model"""

    @staticmethod
    def validate_email(v: str) -> str:
        """Validate email format"""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v.lower()):
            raise ValueError("Invalid email format")

        return v.lower().strip()

    @staticmethod
    def validate_password(v: str) -> str:
        """
        Validate password strength.
        Requirements:
        - Minimum 3 characters
        """
        if not v:
            raise ValueError("Password cannot be empty")

        if len(v) < 3:
            raise ValueError("Password must be at least 8 characters long")

        return v
