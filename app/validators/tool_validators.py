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
        """Convert tool name to lowercase for consistent storage.

        Examples:
        - "GitHub", "github", "GITHUB" -> "github"
        - "VS Code", "vs code" -> "vs code"
        - "Docker" -> "docker"
        """
        if not v:
            return v

        # Convert to lowercase for consistency
        return v.strip().lower()

    @staticmethod
    def validate_uniqueness_check(
        name: str, existing_tools: Optional[list] = None
    ) -> bool:
        """Check if tool name already exists (case-insensitive).

        Args:
            name: Tool name to check
            existing_tools: List of existing tool names to check against

        Returns:
            True if tool is unique

        Raises:
            ValueError: If tool already exists
        """
        if not existing_tools:
            return True

        # Convert to lowercase for comparison
        normalized_name = name.strip().lower()

        # Check against existing tools
        for tool in existing_tools:
            if tool.lower() == normalized_name:
                raise ValueError(
                    f"Tool '{name}' already exists. Tool names must be unique."
                )

        return True
