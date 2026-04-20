import re
from typing import Optional, Dict
from pydantic import ValidationError, field_validator, BaseModel


class AcademicValidator(BaseModel):
    """Validators for Academic model"""

    @staticmethod
    def validate_degree_name(v: str) -> str:
        """Validate degree name"""
        if not v or not v.strip():
            raise ValueError("Degree name cannot be empty")

        if len(v) < 2:
            raise ValueError("Degree name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Degree name must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_college_name(v: str) -> str:
        """Validate college or university name"""
        if not v or not v.strip():
            raise ValueError("College name cannot be empty")

        if len(v) < 2:
            raise ValueError("College name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("College name must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_description(v: Optional[str]) -> Optional[str]:
        """Validate academic description"""
        if v is None:
            return None

        if not v.strip():
            return None

        if len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")

        return v.strip()

    @staticmethod
    def validate_links(v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate academic links"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Links must be a dictionary")

        if len(v) == 0:
            return None

        if len(v) > 10:
            raise ValueError("Cannot exceed 10 academic links")

        # Validate URL format
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
    def validate_month(v: Optional[int]) -> Optional[int]:
        """Validate month value"""
        if v is None:
            return None

        if not isinstance(v, int):
            raise ValueError("Month must be an integer")

        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12")

        return v

    @staticmethod
    def validate_year(v: Optional[int]) -> Optional[int]:
        """Validate year value"""
        if v is None:
            return None

        if not isinstance(v, int):
            raise ValueError("Year must be an integer")

        if v < 1900 or v > 2100:
            raise ValueError("Year must be between 1900 and 2100")

        return v

    @staticmethod
    def validate_date_range(
        start_month: Optional[int],
        start_year: Optional[int],
        end_month: Optional[int],
        end_year: Optional[int],
    ) -> None:
        """Validate that end date is after start date"""
        if start_year and end_year:
            if end_year < start_year:
                raise ValueError("End year cannot be before start year")

            if end_year == start_year and start_month and end_month:
                if end_month < start_month:
                    raise ValueError(
                        "End month cannot be before start month for the same year"
                    )
