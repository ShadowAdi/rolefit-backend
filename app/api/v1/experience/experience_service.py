from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.Profile import Profile
from app.models.User import User
from app.models.Experience import Experience
from app.schema.Experience import ExperienceCreateRequest, ExperienceUpdateRequest
from app.response.experience_responses import (
    ExperienceCreateResponse,
    ExperienceGetResponse,
    ExperienceListResponse,
    ExperienceUpdateResponse,
)
from app.core.logger import logger
from app.validators.experience_validators import ExperienceValidator


class ExperienceServiceClass:
    def create_experience(
        self, db: Session, payload: ExperienceCreateRequest, userId
    ) -> ExperienceCreateResponse:
        """
        Create a new experience record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Verify user has a profile
        5. Create and save the experience record

        Args:
            db: Database session
            payload: ExperienceCreateRequest with experience details
            userId: Authenticated user's ID

        Returns:
            ExperienceCreateResponse with created experience details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting experience creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Experience creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(f"Validating experience creation payload for user {userId}")
                ExperienceValidator.validate_company_name(payload.company_name)
                ExperienceValidator.validate_role(payload.role)
                ExperienceValidator.validate_description(payload.description)
                ExperienceValidator.validate_tech_stack(payload.techStack)
                ExperienceValidator.validate_employment_type(payload.employment_type)
                ExperienceValidator.validate_location_type(payload.location_type)
                ExperienceValidator.validate_location_details(payload.location_details)
                ExperienceValidator.validate_month(payload.start_month)
                ExperienceValidator.validate_year(payload.start_year)
                ExperienceValidator.validate_month(payload.end_month)
                ExperienceValidator.validate_year(payload.end_year)
                ExperienceValidator.validate_date_range(
                    payload.start_month,
                    payload.start_year,
                    payload.end_month,
                    payload.end_year,
                )
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Experience payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "error": str(validation_error),
                        "company": payload.company_name,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Experience creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == userId).first()

            if not user_profile:
                logger.warning(
                    f"Experience creation failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile before adding experience.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Creating experience record for user {userId} at company: {payload.company_name}"
            )

            experience = Experience(
                company_name=payload.company_name,
                description=payload.description,
                role=payload.role,
                techStack=payload.techStack,
                employment_type=payload.employment_type,
                location_type=payload.location_type,
                location_details=payload.location_details,
                start_month=payload.start_month,
                start_year=payload.start_year,
                end_month=payload.end_month,
                end_year=payload.end_year,
                profileId=user_profile.id,
            )

            db.add(experience)
            db.commit()
            db.refresh(experience)

            logger.info(
                f"Experience created successfully",
                extra={
                    "userId": userId,
                    "experienceId": experience.id,
                    "company": experience.company_name,
                    "role": experience.role,
                },
            )

            return ExperienceCreateResponse.model_validate(experience)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "company": payload.company_name if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This experience may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating experience.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the experience.",
            )
