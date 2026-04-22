from typing import Optional
from app.core.AppError import AppError
from app.schema.JobDescription import JobDescriptionCreate, JobDescriptionUpdate


def validate_job_description_create(data: JobDescriptionCreate) -> JobDescriptionCreate:
    """Validate job description creation data"""

    if not data.raw_jd or not data.raw_jd.strip():
        raise AppError(
            status_code=400,
            error_code="INVALID_RAW_JD",
            message="raw_jd is required and cannot be empty",
        )

    if data.salary_min and data.salary_max:
        if not _is_valid_salary_format(data.salary_min):
            raise AppError(
                status_code=400,
                error_code="INVALID_SALARY_MIN",
                message="salary_min format is invalid",
            )
        if not _is_valid_salary_format(data.salary_max):
            raise AppError(
                status_code=400,
                error_code="INVALID_SALARY_MAX",
                message="salary_max format is invalid",
            )

    if data.role_type == "Internship":
        if not data.salary_min and not data.duration:
            raise AppError(
                status_code=400,
                error_code="INTERNSHIP_MISSING_INFO",
                message="For internships, either salary or duration must be provided",
            )

    # Validate that at least one of the optional fields is provided
    has_optional_data = any(
        [
            data.role_name,
            data.company,
            data.location_city,
            data.experience_required,
            data.summary,
        ]
    )

    if not has_optional_data and data.role_type == "Full-time":
        pass

    return data


def validate_job_description_update(data: JobDescriptionUpdate) -> JobDescriptionUpdate:
    """Validate job description update data"""

    if data.salary_min and not _is_valid_salary_format(data.salary_min):
        raise AppError(
            status_code=400,
            error_code="INVALID_SALARY_MIN",
            message="salary_min format is invalid",
        )

    if data.salary_max and not _is_valid_salary_format(data.salary_max):
        raise AppError(
            status_code=400,
            error_code="INVALID_SALARY_MAX",
            message="salary_max format is invalid",
        )

    if data.experience_required and not _is_valid_experience_format(
        data.experience_required
    ):
        raise AppError(
            status_code=400,
            error_code="INVALID_EXPERIENCE_FORMAT",
            message="experience_required format is invalid",
        )

    return data


def _is_valid_salary_format(salary: str) -> bool:
    """
    Validate salary format.
    Supports formats like:
    - "120000"
    - "$120000"
    - "$25-35/week"
    - "25-35"
    """
    if not salary or not salary.strip():
        return False

    salary = salary.strip()

    # Remove common currency symbols
    salary = salary.lstrip("$€£¥")

    # Check if it contains only valid characters (numbers, dash, slash, spaces)
    import re

    pattern = r"^[\d\s\-/.]+$"
    return bool(re.match(pattern, salary))


def _is_valid_experience_format(experience: str) -> bool:
    """
    Validate experience format.
    Supports formats like:
    - "3-5 years"
    - "3 years"
    - "Senior (5+ years)"
    """
    if not experience or not experience.strip():
        return False

    return len(experience.strip()) > 0
