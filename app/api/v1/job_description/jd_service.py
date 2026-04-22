from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from app.models.JobDescription import JobDescription
from app.models.Profile import Profile
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
from app.validators.job_description_validators import (
    validate_job_description_create,
    validate_job_description_update,
)
from typing import List


class JobDescriptionClass:
    def create_jd(
        self, db: Session, userId: str, payload: JobDescriptionCreate
    ) -> JobDescriptionResponse:
        """
        Create a new job description manually (without AI parsing)
        """
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

            try:
                logger.info(
                    f"Validating job description creation request for user: {userId}"
                )
                validate_job_description_create(payload)
            except Exception as validation_error:
                logger.warning(
                    f"JD validation failed for user {userId}: {str(validation_error)}",
                    extra={"userId": userId, "error": str(validation_error)},
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            user = db.query(User).filter(User.id == userId).first()
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
            )

            db.add(new_jd)
            db.commit()
            db.refresh(new_jd)

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

    def get_jd(self, db: Session, jd_id: str, userId: str) -> JobDescriptionResponse:
        """
        Get a specific job description by ID
        """
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

            return format_job_description_response(jd)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving JD for user {userId}: {str(e)}",
                extra={"userId": userId, "jd_id": jd_id, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving job description",
            )

    def get_all_jds(self, db: Session, userId: str) -> List[JobDescriptionResponse]:
        """
        Get all job descriptions for a user
        """
        try:
            if not userId:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

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

            return format_job_descriptions_response(jds)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving JDs for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving job descriptions",
            )

    def update_jd(
        self, db: Session, jd_id: str, userId: str, payload: JobDescriptionUpdate
    ) -> JobDescriptionResponse:
        """
        Update a job description
        """
        try:
            if not jd_id or not userId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job Description ID and User ID are required",
                )

            try:
                logger.info(f"Validating job description update for user: {userId}")
                validate_job_description_update(payload)
            except Exception as validation_error:
                logger.warning(
                    f"JD validation failed for user {userId}: {str(validation_error)}",
                    extra={
                        "userId": userId,
                        "jd_id": jd_id,
                        "error": str(validation_error),
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
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

            db.commit()
            db.refresh(jd)

            logger.info(
                f"Job description updated successfully",
                extra={"userId": userId, "jd_id": jd_id},
            )

            return format_job_description_response(jd)

        except HTTPException:
            raise
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

    def delete_jd(self, db: Session, jd_id: str, userId: str) -> dict:
        """
        Delete a job description
        """
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

            logger.info(
                f"Job description deleted successfully",
                extra={"userId": userId, "jd_id": jd_id},
            )

            return {"message": "Job description deleted successfully"}

        except HTTPException:
            raise
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
