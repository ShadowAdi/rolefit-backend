import re
from typing import Optional
from pydantic import ValidationError, field_validator, BaseModel


class ToolValidator(BaseModel):
    """Validators for Tool model"""

    @staticmethod
    def validate_name(v: str) -> str:
        """Validate tool name"""
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")

        if len(v) < 1:
            raise ValueError("Tool name must be at least 1 character long")

        if len(v) > 255:
            raise ValueError("Tool name must not exceed 255 characters")

        v = v.strip()

        # Allow alphanumeric, spaces, hyphens, periods, and common tool name characters
        if not re.match(r"^[a-zA-Z0-9\s\-.()/&]+$", v):
            raise ValueError(
                "Tool name contains invalid characters. Use alphanumeric, spaces, hyphens, periods, parentheses, slashes, and ampersands."
            )

        return v

    @staticmethod
    def validate_name_format(v: str) -> str:
        """Additional validation to ensure proper tool name format"""
        if not v:
            return v

        # Capitalize first letter of each word
        formatted_name = " ".join(word.capitalize() for word in v.split())

        return formatted_name

    @staticmethod
    def validate_uniqueness_check(
        name: str, existing_tools: Optional[list] = None
    ) -> bool:
        """
        Check if tool name already exists (case-insensitive)
        This should be called before creating a new tool
        """
        if not existing_tools:
            return True

        # Check against existing tools (case-insensitive)
        for tool in existing_tools:
            if tool.lower() == name.lower():
                raise ValueError(
                    f"Tool '{name}' already exists. Tool names must be unique."
                )

        return True
