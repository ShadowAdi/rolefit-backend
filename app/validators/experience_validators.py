import re
from typing import Optional, List
from pydantic import ValidationError, field_validator, BaseModel


class ValidationException(Exception):
    """Custom exception for validation errors with error code"""

    def __init__(
        self, field: str, code: str, message: str, constraint: Optional[str] = None
    ):
        self.field = field
        self.code = code
        self.message = message
        self.constraint = constraint
        super().__init__(self.message)


class ExperienceValidator(BaseModel):
    """Validators for Experience model"""

    @staticmethod
    def validate_company_name(v: str) -> str:
        """Validate company name"""
        if not v or not v.strip():
            raise ValidationException(
                field="company_name",
                code="EMPTY_VALUE",
                message="Company name is required and cannot be empty",
            )

        if len(v) < 2:
            raise ValidationException(
                field="company_name",
                code="TOO_SHORT",
                message="Company name must be at least 2 characters long",
                constraint="min_length: 2",
            )

        if len(v) > 255:
            raise ValidationException(
                field="company_name",
                code="TOO_LONG",
                message="Company name must not exceed 255 characters",
                constraint="max_length: 255",
            )

        return v.strip()

    @staticmethod
    def validate_role(v: str) -> str:
        """Validate job role"""
        if not v or not v.strip():
            raise ValidationException(
                field="role",
                code="EMPTY_VALUE",
                message="Job role is required and cannot be empty",
            )

        if len(v) < 2:
            raise ValidationException(
                field="role",
                code="TOO_SHORT",
                message="Job role must be at least 2 characters long",
                constraint="min_length: 2",
            )

        if len(v) > 255:
            raise ValidationException(
                field="role",
                code="TOO_LONG",
                message="Job role must not exceed 255 characters",
                constraint="max_length: 255",
            )

        return v.strip()

    @staticmethod
    def validate_description(v: str) -> str:
        """Validate experience description"""
        if not v or not v.strip():
            raise ValidationException(
                field="description",
                code="EMPTY_VALUE",
                message="Description is required and cannot be empty",
            )

        if len(v) < 10:
            raise ValidationException(
                field="description",
                code="TOO_SHORT",
                message="Description must be at least 10 characters long",
                constraint="min_length: 10",
            )

        if len(v) > 2000:
            raise ValidationException(
                field="description",
                code="TOO_LONG",
                message="Description must not exceed 2000 characters",
                constraint="max_length: 2000",
            )

        return v.strip()

    @staticmethod
    def validate_tech_stack(v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tech stack list"""
        if v is None:
            return None

        if not isinstance(v, list):
            raise ValidationException(
                field="techStack",
                code="INVALID_TYPE",
                message="Tech stack must be an array of strings",
            )

        if len(v) == 0:
            return None

        if len(v) > 50:
            raise ValidationException(
                field="techStack",
                code="TOO_MANY_ITEMS",
                message="Tech stack cannot exceed 50 items",
                constraint="max_items: 50",
            )

        validated_stack = []
        for i, tech in enumerate(v):
            if not isinstance(tech, str):
                raise ValidationException(
                    field=f"techStack[{i}]",
                    code="INVALID_TYPE",
                    message="Each technology must be a string",
                )

            tech = tech.strip()
            if not tech:
                raise ValidationException(
                    field=f"techStack[{i}]",
                    code="EMPTY_VALUE",
                    message="Technology names cannot be empty",
                )

            if len(tech) > 100:
                raise ValidationException(
                    field=f"techStack[{i}]",
                    code="TOO_LONG",
                    message="Each technology name must not exceed 100 characters",
                    constraint="max_length: 100",
                )

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
            raise ValidationException(
                field="employment_type",
                code="INVALID_VALUE",
                message=f"Employment type must be one of: {', '.join(valid_types)}",
                constraint=f"allowed_values: {', '.join(valid_types)}",
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
            raise ValidationException(
                field="location_type",
                code="INVALID_VALUE",
                message=f"Location type must be one of: {', '.join(valid_types)}",
                constraint=f"allowed_values: {', '.join(valid_types)}",
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
            raise ValidationException(
                field="location_details",
                code="TOO_LONG",
                message="Location details must not exceed 255 characters",
                constraint="max_length: 255",
            )

        return v.strip()

    @staticmethod
    def validate_month(v: Optional[int], field_name: str = "month") -> Optional[int]:
        """Validate month value"""
        if v is None:
            return None

        if not isinstance(v, int):
            raise ValidationException(
                field=field_name,
                code="INVALID_TYPE",
                message="Month must be an integer (1-12)",
            )

        if v < 1 or v > 12:
            raise ValidationException(
                field=field_name,
                code="INVALID_RANGE",
                message="Month must be between 1 and 12",
                constraint="range: 1-12",
            )

        return v

    @staticmethod
    def validate_year(v: Optional[int], field_name: str = "year") -> Optional[int]:
        """Validate year value"""
        if v is None:
            return None

        if not isinstance(v, int):
            raise ValidationException(
                field=field_name,
                code="INVALID_TYPE",
                message="Year must be an integer (1900-2100)",
            )

        if v < 1900 or v > 2100:
            raise ValidationException(
                field=field_name,
                code="INVALID_RANGE",
                message="Year must be between 1900 and 2100",
                constraint="range: 1900-2100",
            )

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
                raise ValidationException(
                    field="end_year",
                    code="INVALID_RANGE",
                    message="End year cannot be before start year",
                )

            if end_year == start_year and start_month and end_month:
                if end_month < start_month:
                    raise ValidationException(
                        field="end_month",
                        code="INVALID_RANGE",
                        message="End month cannot be before start month in the same year",
                    )
