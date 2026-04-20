import re
from typing import Optional, List
from pydantic import ValidationError, field_validator, BaseModel


class ExperienceValidator(BaseModel):
    """Validators for Experience model"""

    @staticmethod
    def validate_company_name(v: str) -> str:
        """Validate company name"""
        if not v or not v.strip():
            raise ValueError("Company name cannot be empty")

        if len(v) < 2:
            raise ValueError("Company name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Company name must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_role(v: str) -> str:
        """Validate job role"""
        if not v or not v.strip():
            raise ValueError("Role cannot be empty")

        if len(v) < 2:
            raise ValueError("Role must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Role must not exceed 255 characters")

        return v.strip()

    @staticmethod
    def validate_description(v: str) -> str:
        """Validate experience description"""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")

        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters long")

        if len(v) > 2000:
            raise ValueError("Description must not exceed 2000 characters")

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
    def validate_employment_type(v: Optional[str]) -> Optional[str]:
        """Validate employment type"""
        if v is None:
            return None

        if not v.strip():
            return None

        valid_types = [
            "Full-time",
            "Part-time",
            "Contract",
            "Temporary",
            "Internship",
            "Freelance",
            "Self-employed",
        ]

        if v not in valid_types:
            raise ValueError(
                f"Invalid employment type. Must be one of: {', '.join(valid_types)}"
            )

        return v

    @staticmethod
    def validate_location_type(v: Optional[str]) -> Optional[str]:
        """Validate location type"""
        if v is None:
            return None

        if not v.strip():
            return None

        valid_types = ["On-site", "Remote", "Hybrid"]

        if v not in valid_types:
            raise ValueError(
                f"Invalid location type. Must be one of: {', '.join(valid_types)}"
            )

        return v

    @staticmethod
    def validate_location_details(v: Optional[str]) -> Optional[str]:
        """Validate location details"""
        if v is None:
            return None

        if not v.strip():
            return None

        if len(v) > 255:
            raise ValueError("Location details must not exceed 255 characters")

        return v.strip()

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
