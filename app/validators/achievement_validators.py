import re
from typing import Optional, Dict
from pydantic import ValidationError, field_validator, BaseModel


class AchievementValidator(BaseModel):
    """Validators for Achievement model"""

    @staticmethod
    def validate_title(v: str) -> str:
        """Validate achievement title"""
        if not v or not v.strip():
            raise ValueError("Achievement title cannot be empty")

        if len(v) < 3:
            raise ValueError("Achievement title must be at least 3 characters long")

        if len(v) > 255:
            raise ValueError("Achievement title must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_achievement_type(v: str) -> str:
        """Validate achievement type"""
        if not v or not v.strip():
            raise ValueError("Achievement type cannot be empty")

        if len(v) < 2:
            raise ValueError("Achievement type must be at least 2 characters long")

        if len(v) > 100:
            raise ValueError("Achievement type must not exceed 100 characters")

        # Valid types
        valid_types = [
            "Award",
            "Certification",
            "Recognition",
            "Medal",
            "Scholarship",
            "Honour",
            "Badge",
            "License",
            "Other",
        ]

        v_stripped = v.strip()
        # Allow custom types but validate common ones
        if v_stripped not in valid_types:
            # Allow custom types with alphanumeric and spaces
            if not re.match(r"^[a-zA-Z0-9\s\-&.]+$", v_stripped):
                raise ValueError(
                    f"Achievement type contains invalid characters. Use alphanumeric characters, spaces, hyphens, ampersands, and periods."
                )

        return v_stripped

    @staticmethod
    def validate_description(v: str) -> str:
        """Validate achievement description"""
        if not v or not v.strip():
            raise ValueError("Achievement description cannot be empty")

        if len(v) < 10:
            raise ValueError(
                "Achievement description must be at least 10 characters long"
            )

        if len(v) > 2000:
            raise ValueError("Achievement description must not exceed 2000 characters")

        return v.strip()

    @staticmethod
    def validate_location(v: Optional[str]) -> Optional[str]:
        """Validate achievement location"""
        if v is None:
            return None

        if not v.strip():
            return None

        if len(v) > 255:
            raise ValueError("Location must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_month(v: Optional[str]) -> Optional[str]:
        """Validate month value"""
        if v is None:
            return None

        if not v.strip():
            return None

        v = v.strip()

        # Valid month names and abbreviations
        valid_months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Sept",
            "Oct",
            "Nov",
            "Dec",
        ]

        if v not in valid_months:
            raise ValueError(
                f"Invalid month '{v}'. Use full month name or 3-letter abbreviation."
            )

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
    def validate_links(v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate achievement links"""
        if v is None:
            return None

        if not isinstance(v, dict):
            raise ValueError("Links must be a dictionary")

        if len(v) == 0:
            return None

        if len(v) > 10:
            raise ValueError("Cannot exceed 10 achievement links")

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
    def validate_date_range(
        start_month: Optional[str],
        start_year: Optional[int],
        end_month: Optional[str],
        end_year: Optional[int],
    ) -> None:
        """Validate that end date is after start date"""
        if start_year and end_year:
            if end_year < start_year:
                raise ValueError("End year cannot be before start year")

            if end_year == start_year and start_month and end_month:
                # Simple month comparison based on order
                month_order = {
                    "january": 1,
                    "february": 2,
                    "march": 3,
                    "april": 4,
                    "may": 5,
                    "june": 6,
                    "july": 7,
                    "august": 8,
                    "september": 9,
                    "october": 10,
                    "november": 11,
                    "december": 12,
                    "jan": 1,
                    "feb": 2,
                    "mar": 3,
                    "apr": 4,
                    "may": 5,
                    "jun": 6,
                    "jul": 7,
                    "aug": 8,
                    "sep": 9,
                    "sept": 9,
                    "oct": 10,
                    "nov": 11,
                    "dec": 12,
                }

                start_month_num = month_order.get(start_month.lower())
                end_month_num = month_order.get(end_month.lower())

                if (
                    start_month_num
                    and end_month_num
                    and end_month_num < start_month_num
                ):
                    raise ValueError(
                        "End month cannot be before start month for the same year"
                    )
