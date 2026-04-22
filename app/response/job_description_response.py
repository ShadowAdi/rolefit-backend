from typing import List, Optional
from app.schema.JobDescription import JobDescriptionResponse
from app.models.JobDescription import JobDescription


def format_job_description_response(
    job_description: JobDescription,
) -> JobDescriptionResponse:
    """
    Format a JobDescription model instance into a response schema
    """
    return JobDescriptionResponse(
        id=str(job_description.id),
        role_name=job_description.Role_Name,
        company=job_description.Company,
        role_type=(
            job_description.Role_Type.value if job_description.Role_Type else None
        ),
        location=job_description.Location.value if job_description.Location else None,
        location_city=job_description.Location_City,
        salary_min=job_description.Salary_Min,
        salary_max=job_description.Salary_Max,
        salary_currency=job_description.Salary_Currency,
        duration=job_description.Duration,
        tech_stack=job_description.Tech_Stack or [],
        required_skills=job_description.Required_Skills or [],
        experience_required=job_description.Experience_Required,
        summary=job_description.Summary,
        raw_jd=job_description.Raw_JD,
        created_at=job_description.Created_At,
        updated_at=job_description.Updated_At,
    )


def format_job_descriptions_response(
    job_descriptions: List[JobDescription],
) -> List[JobDescriptionResponse]:
    """
    Format a list of JobDescription model instances into response schemas
    """
    return [format_job_description_response(jd) for jd in job_descriptions]


def create_job_description_response(
    id: str,
    role_name: Optional[str],
    company: Optional[str],
    role_type: Optional[str],
    location: Optional[str],
    location_city: Optional[str],
    salary_min: Optional[str],
    salary_max: Optional[str],
    salary_currency: Optional[str],
    duration: Optional[str],
    tech_stack: List[str],
    required_skills: List[str],
    experience_required: Optional[str],
    summary: Optional[str],
    raw_jd: str,
    created_at,
    updated_at,
) -> JobDescriptionResponse:
    """
    Create a JobDescriptionResponse from individual fields
    """
    return JobDescriptionResponse(
        id=id,
        role_name=role_name,
        company=company,
        role_type=role_type,
        location=location,
        location_city=location_city,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        duration=duration,
        tech_stack=tech_stack,
        required_skills=required_skills,
        experience_required=experience_required,
        summary=summary,
        raw_jd=raw_jd,
        created_at=created_at,
        updated_at=updated_at,
    )
