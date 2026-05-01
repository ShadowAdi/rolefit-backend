from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status,ValidationError
from uuid import UUID
import json
from app.models.JobDescription import JobDescription
from app.models.User import User
from app.core.logger import logger
from app.models.Experience import Experience
from app.models.Achievement import Achievement
from app.models.Project import Project
from app.models.Publication import Publication
from app.models.Skill import Skill
from app.models.Tool import Tool
from app.models.Academic import Academic
from app.models.UserSkill import UserSkill
from app.models.UserTool import UserTool
from typing import Dict, Any
from app.helpers.db_helpers import get_user_profile
from app.helpers.redis_cache_helpers import get_cache, set_cache


async def filter_jd(
    jobId: str, userId: str, content_type: str, db: Session
) -> Dict[str, Any]:
    try:
        if not jobId or not isinstance(jobId, str):
            logger.error(
                "Failed to filter Job based on job. Job Id Was not given",
                extra={"jobId": jobId},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job ID is required and must be a valid string",
            )
        if not userId or not isinstance(userId, str):
            logger.error(
                "Failed to filter Job based on profile. User Id was not given",
                extra={"userId": userId},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required and must be a valid string",
            )

        # Try cache first - job profile is shared across all content for a job
        cache_key = f"job-profile-data-{jobId}-{userId}"
        cached_data = get_cache(cache_key)
        if cached_data:
            logger.info(f"Job profile data retrieved from cache for jobId={jobId}")
            return json.loads(cached_data)

        user = db.query(User).filter(User.id == userId).first()
        if not user:
            logger.warning(
                "User not found",
                extra={"userId": userId},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist",
            )

        user_profile = await get_user_profile(db, userId)

        jd = (
            db.query(JobDescription)
            .filter(
                JobDescription.id == jobId,
                JobDescription.userId == userId,
            )
            .first()
        )

        if not jd:
            logger.warning(
                "Job description not found",
                extra={"userId": userId, "jd_id": jobId},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found",
            )

        try:
            experiences = (
                db.query(Experience)
                .filter(Experience.profileId == user_profile.id)
                .all()
            )

            achievements = (
                db.query(Achievement)
                .filter(Achievement.profileId == user_profile.id)
                .all()
            )

            projects = (
                db.query(Project).filter(Project.profileId == user_profile.id).all()
            )

            publications = (
                db.query(Publication)
                .filter(Publication.profileId == user_profile.id)
                .all()
            )

            academics = (
                db.query(Academic).filter(Academic.profileId == user_profile.id).all()
            )

            user_skills = (
                db.query(Skill)
                .join(UserSkill, Skill.id == UserSkill.skillId)
                .filter(UserSkill.userId == user.id)
                .all()
            )

            user_tools = (
                db.query(Tool)
                .join(UserTool, Tool.id == UserTool.toolId)
                .filter(UserTool.userId == user.id)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error while fetching user data",
                extra={"userId": userId, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user data from database",
            )

        job_description_data = {
            "id": str(jd.id),
            "role_name": jd.Role_Name,
            "company": jd.Company,
            "role_type": jd.Role_Type.value if jd.Role_Type else None,
            "location": jd.Location.value if jd.Location else None,
            "location_city": jd.Location_City,
            "salary_min": jd.Salary_Min,
            "salary_max": jd.Salary_Max,
            "salary_currency": jd.Salary_Currency,
            "duration": jd.Duration,
            "tech_stack": jd.Tech_Stack,
            "required_skills": jd.Required_Skills,
            "experience_required": jd.Experience_Required,
            "summary": jd.Summary,
            "raw_jd": jd.Raw_JD,
        }

        user_data_dict = {
            "user": {
                "id": str(user.id),
                "email": user.email,
            },
            "profile": {
                "id": str(user_profile.id),
                "full_name": user_profile.full_name,
                "headline": user_profile.headline,
                "summary": user_profile.summary,
                "resume_link": user_profile.resume_link,
                "cover_letter_link": user_profile.cover_letter_link,
                "links": user_profile.links,
            },
            "experiences": [
                {
                    "id": str(exp.id),
                    "company_name": exp.company_name,
                    "role": exp.role,
                    "description": exp.description,
                    "employment_type": exp.employment_type,
                    "location_type": exp.location_type,
                    "location_details": exp.location_details,
                    "start_month": exp.start_month,
                    "start_year": exp.start_year,
                    "end_month": exp.end_month,
                    "end_year": exp.end_year,
                    "priority": exp.priority,
                    "techStack": exp.techStack,
                }
                for exp in experiences
            ],
            "achievements": [
                {
                    "id": str(ach.id),
                    "title": ach.title,
                    "achievement_type": ach.achievement_type,
                    "description": ach.description,
                    "location": ach.location,
                    "start_month": ach.start_month,
                    "start_year": ach.start_year,
                    "end_month": ach.end_month,
                    "end_year": ach.end_year,
                    "priority": ach.priority,
                    "links": ach.links,
                }
                for ach in achievements
            ],
            "projects": [
                {
                    "id": str(proj.id),
                    "title": proj.title,
                    "description": proj.description,
                    "techStack": proj.techStack,
                    "links": proj.links,
                    "priority": proj.priority,
                    "startDate": proj.startDate.isoformat() if proj.startDate else None,
                    "endDate": proj.endDate.isoformat() if proj.endDate else None,
                }
                for proj in projects
            ],
            "publications": [
                {
                    "id": str(pub.id),
                    "title": pub.title,
                    "publisher": pub.publisher,
                    "publication_date": (
                        pub.publication_date.isoformat()
                        if pub.publication_date
                        else None
                    ),
                    "authors": pub.authors,
                    "description": pub.description,
                    "priority": pub.priority,
                    "url": pub.url,
                }
                for pub in publications
            ],
            "academics": [
                {
                    "id": str(acad.id),
                    "degree_name": acad.degree_name,
                    "college_name": acad.college_name,
                    "description": acad.description,
                    "start_month": acad.start_month,
                    "start_year": acad.start_year,
                    "end_month": acad.end_month,
                    "end_year": acad.end_year,
                    "priority": acad.priority,
                    "links": acad.links,
                }
                for acad in academics
            ],
            "skills": [
                {
                    "id": str(skill.id),
                    "name": skill.name,
                }
                for skill in user_skills
            ],
            "tools": [
                {
                    "id": str(tool.id),
                    "name": tool.name,
                }
                for tool in user_tools
            ],
            "job_description": job_description_data,
        }

        if content_type != "Resume":
            job_description_data.update(
                {
                    "company_name": jd.CompanyName if jd.CompanyName else None,
                    "company_information": (
                        jd.CompanyInformation if jd.CompanyInformation else None
                    ),
                    "company_website_url": (
                        jd.CompanyWebsiteUrl if jd.CompanyWebsiteUrl else None
                    ),
                }
            )

        logger.info(
            "Successfully compiled user data for resume/cover letter generation",
            extra={"userId": userId, "jobId": jobId},
        )

        # Cache the compiled job profile data for 6 hours (won't change unless JD is updated)
        set_cache(cache_key, json.dumps(user_data_dict), ttl=21600)

        return user_data_dict

    except HTTPException:
        raise
    except ValidationError as ve:
        logger.error(
            "Validation error during job description filter",
            extra={"userId": userId, "jobId": jobId, "validation_errors": str(ve)},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data format in request",
        )
    except IntegrityError as ie:
        logger.error(
            "Database integrity error during filter operation",
            extra={"userId": userId, "jobId": jobId, "error": str(ie)},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity constraint violated",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during job description filter: {str(e)}",
            extra={"userId": userId, "jobId": jobId, "error_type": type(e).__name__},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process job description filter",
        )
