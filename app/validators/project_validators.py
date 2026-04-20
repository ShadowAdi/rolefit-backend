import re
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import ValidationError, field_validator, BaseModel


class ProjectValidator(BaseModel):
    """Validators for Project model"""

    @staticmethod
    def validate_title(v: str) -> str:
        """Validate project title"""
        if not v or not v.strip():
            raise ValueError("Project title cannot be empty")

        if len(v) < 3:
            raise ValueError("Project title must be at least 3 characters long")

        if len(v) > 255:
            raise ValueError("Project title must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_description(v: str) -> str:
        """Validate project description"""
        if not v or not v.strip():
            raise ValueError("Project description cannot be empty")

        if len(v) < 10:
            raise ValueError("Project description must be at least 10 characters long")

        if len(v) > 2000:
            raise ValueError("Project description must not exceed 2000 characters")

        return v.strip()

    @staticmethod
    def validate_tech_stack(v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tech stack list"""
        if v is None:
            return None

        if not isinstance(v, list):
            raise ValueError("Tech stack must be a list")

        if len(v) == 0:
            return None

        if len(v) > 50:
            raise ValueError("Tech stack cannot exceed 50 items")

        validated_stack = []
        for tech in v:
            if not isinstance(tech, str):
                raise ValueError("Each tech stack item must be a string")

            tech = tech.strip()
            if not tech:
                raise ValueError("Tech stack items cannot be empty")

            if len(tech) > 100:
                raise ValueError("Each tech stack item must not exceed 100 characters")

            validated_stack.append(tech)

        return validated_stack if validated_stack else None

    @staticmethod
    def validate_links(v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate project links"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Links must be a dictionary")

        if len(v) == 0:
            return None

        if len(v) > 10:
            raise ValueError("Cannot exceed 10 project links")

        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"

        validated_links = {}
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Link key must be a string, got {type(key).__name__}")

            if not isinstance(value, str):
                raise ValueError(f"Link value must be a string for key '{key}'")

            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError("Link key cannot be empty")

            if not value:
                raise ValueError(f"Link value for '{key}' cannot be empty")

            if len(key) > 100:
                raise ValueError(f"Link key '{key}' must not exceed 100 characters")

            if len(value) > 2000:
                raise ValueError(
                    f"Link value for '{key}' must not exceed 2000 characters"
                )

            if not re.match(url_pattern, value):
                raise ValueError(f"Invalid URL format for '{key}': {value}")

            validated_links[key] = value

        return validated_links if validated_links else None

    @staticmethod
    def validate_start_date(v: Optional[datetime]) -> Optional[datetime]:
        """Validate project start date"""
        if v is None:
            return None

        if not isinstance(v, datetime):
            raise ValueError("Start date must be a datetime object")

        return v

    @staticmethod
    def validate_end_date(v: Optional[datetime]) -> Optional[datetime]:
        """Validate project end date"""
        if v is None:
            return None

        if not isinstance(v, datetime):
            raise ValueError("End date must be a datetime object")

        return v

    @staticmethod
    def validate_date_range(
        start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> None:
        """Validate that end date is after start date"""
        if start_date and end_date:
            if end_date < start_date:
                raise ValueError("End date cannot be before start date")

            if end_date == start_date:
                raise ValueError("End date must be after start date")
