import os
import requests
import json
import re
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from app.models.JobDescription import JobDescription, RoleTypeEnum, LocationTypeEnum
from app.models.User import User
from app.schema.JobDescription import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
)
from app.response.job_description_response import (
    format_job_description_response,
    format_job_descriptions_response,
)
from app.core.logger import logger
from app.core.AppError import AppError
from app.validators.job_description_validators import (
    validate_job_description_create,
    validate_job_description_update,
)
from app.helpers.jd_parser import JDParseError, parse_jd_with_ai
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache
from typing import List


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JobDescriptionClass:
    async def create_jd(
        self, db: Session, userId: str, payload: JobDescriptionCreate
    ) -> JobDescriptionResponse:

        try:
            if not userId:
                logger.error(
                    "JD creation failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            logger.info(
                f"Validating job description creation request for user: {userId}"
            )
            validate_job_description_create(payload)

            user = db.query(User).filter(User.id == UUID(userId)).first()
            if not user:
                logger.warning(
                    "JD creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            role_name_lower = (
                payload.role_name.lower().strip() if payload.role_name else None
            )
            company_lower = payload.company.lower().strip() if payload.company else None

            if role_name_lower and company_lower:
                existing_jd = (
                    db.query(JobDescription)
                    .filter(
                        JobDescription.userId == UUID(userId),
                        JobDescription.Role_Name.ilike(role_name_lower),
                        JobDescription.Company.ilike(company_lower),
                    )
                    .first()
                )

                if existing_jd:
                    logger.warning(
                        f"JD creation failed: Duplicate job description already exists",
                        extra={
                            "userId": userId,
                            "role_name": role_name_lower,
                            "company": company_lower,
                        },
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"A job description for '{payload.role_name}' at '{payload.company}' already exists. Please use a different role or company.",
                    )

            new_jd = JobDescription(
                userId=UUID(userId),
                Role_Name=role_name_lower,
                Company=company_lower,
                Role_Type=payload.role_type,
                Location=payload.location,
                Location_City=(
                    payload.location_city.lower().strip()
                    if payload.location_city
                    else None
                ),
                Salary_Min=payload.salary_min,
                Salary_Max=payload.salary_max,
                Salary_Currency=(
                    payload.salary_currency.upper().strip()
                    if payload.salary_currency
                    else None
                ),
                Duration=payload.duration,
                Tech_Stack=(
                    [tech.strip().lower() for tech in payload.tech_stack]
                    if payload.tech_stack
                    else []
                ),
                Required_Skills=(
                    [skill.strip().lower() for skill in payload.required_skills]
                    if payload.required_skills
                    else []
                ),
                Experience_Required=(
                    payload.experience_required.lower().strip()
                    if payload.experience_required
                    else None
                ),
                Summary=payload.summary.strip() if payload.summary else None,
                Raw_JD=payload.raw_jd.strip(),
                CompanyName=(
                    payload.company_name.strip() if payload.company_name else None
                ),
                CompanyInformation=(
                    payload.company_information.strip()
                    if payload.company_information
                    else None
                ),
                CompanyWebsiteUrl=(
                    payload.company_website_url.strip()
                    if payload.company_website_url
                    else None
                ),
            )

            db.add(new_jd)
            db.commit()
            db.refresh(new_jd)

            # Invalidate user's JDs list cache since we added a new one
            await delete_cache(f"jds-{userId}")

            logger.info(
                f"Job description created successfully for user {userId}",
                extra={
                    "userId": userId,
                    "jd_id": str(new_jd.id),
                    "role_name": new_jd.Role_Name,
                    "company": new_jd.Company,
                },
            )

            return format_job_description_response(new_jd)

        except HTTPException:
            raise
        except AppError as e:
            logger.warning(
                f"Validation error during JD creation for user {userId}: {e.message}",
                extra={"userId": userId, "error_code": e.error_code},
            )
            raise HTTPException(
                status_code=e.status_code,
                detail=e.message,
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error during JD creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. Please ensure all required fields are valid.",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during JD creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating job description",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during JD creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating job description",
            )

    async def get_jd(
        self, db: Session, jd_id: str, userId: str
    ) -> JobDescriptionResponse:

        try:
            if not jd_id or not userId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job Description ID and User ID are required",
                )

            # Try cache first
            cache_key = f"jd-{userId}-{jd_id}"
            cached_jd = await get_cache(cache_key)
            if cached_jd:
                logger.info(
                    f"Job description retrieved from cache",
                    extra={"userId": userId, "jd_id": jd_id},
                )
                return json.loads(cached_jd)

            jd = (
                db.query(JobDescription)
                .filter(
                    JobDescription.id == UUID(jd_id),
                    JobDescription.userId == UUID(userId),
                )
                .first()
            )

            if not jd:
                logger.warning(
                    f"JD not found",
                    extra={"userId": userId, "jd_id": jd_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found",
                )

            logger.info(
                f"Job description retrieved successfully",
                extra={"userId": userId, "jd_id": jd_id},
            )

            response = format_job_description_response(jd)
            # Convert Pydantic model to dict for JSON serialization
            response_dict = (
                response.model_dump()
                if hasattr(response, "model_dump")
                else response.dict()
            )
            await set_cache(
                cache_key, json.dumps(response_dict, cls=DateTimeEncoder), ttl=3600
            )
            return response

        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(
                f"Invalid UUID format for JD retrieval",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Job Description ID or User ID format",
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error retrieving JD for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving job description",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving JD for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving job description",
            )

    async def get_all_jds(
        self, db: Session, userId: str
    ) -> List[JobDescriptionResponse]:

        try:
            if not userId:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            # Try cache first
            cache_key = f"jds-{userId}"
            cached_jds = await get_cache(cache_key)
            if cached_jds:
                logger.info(
                    f"Retrieved job descriptions from cache for user",
                    extra={"userId": userId},
                )
                return json.loads(cached_jds)

            jds = (
                db.query(JobDescription)
                .filter(JobDescription.userId == UUID(userId))
                .order_by(JobDescription.Created_At.desc())
                .all()
            )

            logger.info(
                f"Retrieved {len(jds)} job descriptions for user",
                extra={"userId": userId, "count": len(jds)},
            )

            response = format_job_descriptions_response(jds)
            # Convert Pydantic models to dicts for JSON serialization
            response_dicts = [
                item.model_dump() if hasattr(item, "model_dump") else item.dict()
                for item in response
            ]
            await set_cache(
                cache_key, json.dumps(response_dicts, cls=DateTimeEncoder), ttl=3600
            )
            return response

        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(
                f"Invalid UUID format for user: {str(e)} userId: {userId}",
                extra={"userId": userId},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid User ID format",
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error retrieving JDs for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving job descriptions",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving JDs for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving job descriptions",
            )

    async def update_jd(
        self, db: Session, jd_id: str, userId: str, payload: JobDescriptionUpdate
    ) -> JobDescriptionResponse:

        try:
            if not jd_id or not userId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job Description ID and User ID are required",
                )

            logger.info(f"Validating job description update for user: {userId}")
            validate_job_description_update(payload)

            jd = (
                db.query(JobDescription)
                .filter(
                    JobDescription.id == UUID(jd_id),
                    JobDescription.userId == UUID(userId),
                )
                .first()
            )

            if not jd:
                logger.warning(
                    f"JD not found for update",
                    extra={"userId": userId, "jd_id": jd_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found",
                )

            if payload.role_name or payload.company:
                role_name_lower = (payload.role_name or jd.Role_Name).lower().strip()
                company_lower = (payload.company or jd.Company).lower().strip()

                existing_jd = (
                    db.query(JobDescription)
                    .filter(
                        JobDescription.userId == UUID(userId),
                        JobDescription.id != UUID(jd_id),
                        JobDescription.Role_Name.ilike(role_name_lower),
                        JobDescription.Company.ilike(company_lower),
                    )
                    .first()
                )

                if existing_jd:
                    logger.warning(
                        f"JD update failed: Duplicate job description exists",
                        extra={
                            "userId": userId,
                            "jd_id": jd_id,
                            "role_name": role_name_lower,
                            "company": company_lower,
                        },
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Another job description with the same role and company already exists",
                    )

            if payload.role_name:
                jd.Role_Name = payload.role_name.lower().strip()
            if payload.company:
                jd.Company = payload.company.lower().strip()
            if payload.role_type:
                jd.Role_Type = payload.role_type
            if payload.location:
                jd.Location = payload.location
            if payload.location_city:
                jd.Location_City = payload.location_city.lower().strip()
            if payload.salary_min:
                jd.Salary_Min = payload.salary_min
            if payload.salary_max:
                jd.Salary_Max = payload.salary_max
            if payload.salary_currency:
                jd.Salary_Currency = payload.salary_currency.upper().strip()
            if payload.duration:
                jd.Duration = payload.duration
            if payload.tech_stack is not None:
                jd.Tech_Stack = [tech.strip().lower() for tech in payload.tech_stack]
            if payload.required_skills is not None:
                jd.Required_Skills = [
                    skill.strip().lower() for skill in payload.required_skills
                ]
            if payload.experience_required:
                jd.Experience_Required = payload.experience_required.lower().strip()
            if payload.summary:
                jd.Summary = payload.summary.strip()
            if payload.raw_jd:
                jd.Raw_JD = payload.raw_jd.strip()
            if payload.company_website_url:
                jd.CompanyWebsiteUrl = payload.company_website_url.strip()
            if payload.company_name:
                jd.CompanyName = payload.company_name.strip()
            if payload.company_information:
                jd.CompanyInformation = payload.company_information.strip()

            db.commit()
            db.refresh(jd)

            # Invalidate caches
            await delete_cache(f"jd-{userId}-{jd_id}")
            await delete_cache(f"jds-{userId}")

            logger.info(
                f"Job description updated successfully",
                extra={"userId": userId, "jd_id": jd_id},
            )

            return format_job_description_response(jd)

        except HTTPException:
            raise
        except AppError as e:
            logger.warning(
                f"Validation error during JD update for user {userId}: {e.message}",
                extra={"userId": userId, "jd_id": jd_id, "error_code": e.error_code},
            )
            raise HTTPException(
                status_code=e.status_code,
                detail=e.message,
            )
        except ValueError as e:
            logger.warning(
                f"Invalid UUID format for JD update",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Job Description ID or User ID format",
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error during JD update for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during JD update for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating job description",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during JD update for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating job description",
            )

    async def delete_jd(self, db: Session, jd_id: str, userId: str) -> dict:
        try:
            if not jd_id or not userId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job Description ID and User ID are required",
                )

            jd = (
                db.query(JobDescription)
                .filter(
                    JobDescription.id == UUID(jd_id),
                    JobDescription.userId == UUID(userId),
                )
                .first()
            )

            if not jd:
                logger.warning(
                    f"JD not found for deletion",
                    extra={"userId": userId, "jd_id": jd_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found",
                )

            db.delete(jd)
            db.commit()

            # Invalidate caches
            await delete_cache(f"jd-{userId}-{jd_id}")
            await delete_cache(f"jds-{userId}")

            logger.info(
                f"Job description deleted successfully",
                extra={"userId": userId, "jd_id": jd_id},
            )

            return {"message": "Job description deleted successfully"}

        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(
                f"Invalid UUID format for JD deletion",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Job Description ID or User ID format",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during JD deletion for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting job description",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during JD deletion for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting job description",
            )

    async def generate_jd(
        self, db: Session, userId: str, raw_jd: str
    ) -> JobDescriptionResponse:

        try:
            if not userId:
                logger.error(
                    "JD generation failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            if not raw_jd or not raw_jd.strip():
                logger.warning(
                    "JD generation failed: Empty raw JD",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Raw job description cannot be empty",
                )

            logger.info(f"Generating job description from raw JD for user: {userId}")

            # Create hash of raw JD for caching parsed results
            raw_jd_hash = hashlib.md5(raw_jd.strip().encode()).hexdigest()
            cache_key = f"jd-parse-{raw_jd_hash}"

            # Try to get cached parse result
            cached_parse = await get_cache(cache_key)
            if cached_parse:
                parsed_data = json.loads(cached_parse)
                logger.info(
                    f"Using cached JD parse result for user: {userId}",
                    extra={"userId": userId},
                )
            else:
                parsed_data = parse_jd_with_ai(raw_jd)
                # Cache the parse result for 24 hours (expensive AI operation)
                await set_cache(cache_key, json.dumps(parsed_data), ttl=86400)

            logger.debug(f"Parsed role_name: {parsed_data.get('role_name')}")

            jd_payload = JobDescriptionCreate(
                user_id=userId,
                role_name=parsed_data.get("role_name"),
                company=parsed_data.get("company"),
                role_type=parsed_data.get("role_type"),
                location=parsed_data.get("location"),
                location_city=parsed_data.get("location_city"),
                salary_min=(
                    str(parsed_data["salary_min"])
                    if parsed_data.get("salary_min") is not None
                    else None
                ),
                salary_max=(
                    str(parsed_data["salary_max"])
                    if parsed_data.get("salary_max") is not None
                    else None
                ),
                salary_currency=parsed_data.get("salary_currency"),
                duration=parsed_data.get("duration"),
                tech_stack=parsed_data.get("tech_stack", []),
                required_skills=parsed_data.get("required_skills", []),
                experience_required=parsed_data.get("experience_required"),
                summary=parsed_data.get("summary"),
                raw_jd=raw_jd.strip(),
            )

            logger.info(
                f"Creating JD from AI-parsed data for user: {userId}",
                extra={
                    "userId": userId,
                    "company": jd_payload.company,
                    "role_name": jd_payload.role_name,
                },
            )

            return await self.create_jd(db, userId, jd_payload)

        except HTTPException:
            raise
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON parsing error during JD generation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error parsing AI response. Please try again.",
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"API request error during JD generation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to parse job description. Please try again later.",
            )

        except JDParseError as e:
            logger.warning(
                f"AI JD parsing failed for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not parse the job description into structured data. Please try again.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during JD generation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while generating job description",
            )

    def test_jd(self, db: Session, userId: str):
        try:
            if not userId:
                logger.error(
                    f"Job creation failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            payload = "Junior Software Engineer $60k – $70k About the job About the role: We're building TrickCV.com , an AI-powered Chrome extension that tailors your CV to any job description in one click. Live product, real traction, growing fast. Looking for a junior engineer to help us scale. What you'll work on: Chrome extension development and improvements Backend APIs and automation pipelines AI model integrations Shipping fast with direct founder collaboration What we're looking for: 1+ years experience in JavaScript or Python Comfortable working independently and remotely Interest in AI or productivity tools is a big plus Chrome extension or LLM experience is a bonus — not required  What we offer:  Fully remote, flexible hours Direct impact — small team, your work ships immediately Equity discussion possible for the right person Competitive salary for early stage Visit us : trickcv.com"

            parsed_data = parse_jd_with_ai(payload)

            print(f"this is the parsed response {parsed_data}")
            return True

        except Exception as e:
            logger.error(f"Failed to test the jd: {e}")
            raise HTTPException("Failed to test the jd", 500)
