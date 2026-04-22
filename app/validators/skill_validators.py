import re
from typing import Optional
from pydantic import ValidationError, field_validator, BaseModel


class SkillValidator(BaseModel):
    """Validators for Skill model"""

    @staticmethod
    def validate_name(v: str) -> str:
        """Validate skill name"""
        if not v or not v.strip():
            raise ValueError("Skill name cannot be empty")

        if len(v) < 1:
            raise ValueError("Skill name must be at least 1 character long")

        if len(v) > 255:
            raise ValueError("Skill name must not exceed 255 characters")

        v = v.strip()

        # Allow alphanumeric, spaces, hyphens, plus signs, periods, and hashtags
        # Common for programming skills like C++, C#, .NET, etc.
        if not re.match(r"^[a-zA-Z0-9\s\-+.#]+$", v):
            raise ValueError(
                "Skill name contains invalid characters. Use alphanumeric, spaces, hyphens, plus signs, periods, and hashtags."
            )

        return v

    @staticmethod
    def validate_name_format(v: str) -> str:
        """Convert skill name to lowercase for consistent storage.

        Examples:
        - "Frontend", "frontend", "FRONTEND" -> "frontend"
        - "REST API", "rest api" -> "rest api"
        - "Web Design" -> "web design"
        """
        if not v:
            return v

        # Convert to lowercase for consistency
        return v.strip().lower()

    @staticmethod
    def validate_uniqueness_check(
        name: str, existing_skills: Optional[list] = None
    ) -> bool:
        """Check if skill name already exists (case-insensitive).

        Args:
            name: Skill name to check
            existing_skills: List of existing skill names to check against

        Returns:
            True if skill is unique

        Raises:
            ValueError: If skill already exists
        """
        if not existing_skills:
            return True

        # Convert to lowercase for comparison
        normalized_name = name.strip().lower()

        # Check against existing skills
        for skill in existing_skills:
            if skill.lower() == normalized_name:
                raise ValueError(
                    f"Skill '{name}' already exists. Skill names must be unique."
                )

        return True
