import re
from typing import Optional, Dict, Any
from pydantic import ValidationError, field_validator, BaseModel


class ProfileValidator(BaseModel):
    """Validators for Profile model"""

    @staticmethod
    def validate_full_name(v: str) -> str:
        """Validate full name format"""
        if not v or not v.strip():
            raise ValueError("Full name cannot be empty")

        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Full name must not exceed 255 characters")

        name_pattern = r"^[a-zA-Z\s\-']{2,255}$"
        if not re.match(name_pattern, v):
            raise ValueError("Full name contains invalid characters")

        return v.strip()

    @staticmethod
    def validate_headline(v: str) -> str:
        """Validate professional headline format"""
        if not v or not v.strip():
            raise ValueError("Headline cannot be empty")

        if len(v) < 5:
            raise ValueError("Headline must be at least 5 characters long")

        if len(v) > 255:
            raise ValueError("Headline must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_summary(v: Optional[str]) -> Optional[str]:
        """Validate professional summary format"""
        if v is None:
            return None

        if not v.strip():
            return None

        if len(v) > 2000:
            raise ValueError("Summary must not exceed 2000 characters")

        return v.strip()

    @staticmethod
    def validate_links(v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate links object"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Links must be a dictionary")

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"

        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Link key must be a string, got {type(key).__name__}")

            if isinstance(value, str):
                if not re.match(url_pattern, value):
                    raise ValueError(f"Invalid URL format for '{key}': {value}")
            elif not isinstance(value, (str, dict, list)):
                raise ValueError(
                    f"Link value for '{key}' must be a string, dict, or list"
                )

        return v
