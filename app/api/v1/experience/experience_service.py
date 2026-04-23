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
from app.validators.experience_validators import (
    ExperienceValidator,
    ValidationException,
)
from app.core.validation_error import ValidationErrorField, ValidationErrorResponse


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
                ExperienceValidator.validate_month(payload.start_month, "start_month")
                ExperienceValidator.validate_year(payload.start_year, "start_year")
                ExperienceValidator.validate_month(payload.end_month, "end_month")
                ExperienceValidator.validate_year(payload.end_year, "end_year")
                ExperienceValidator.validate_priority(payload.priority)
                ExperienceValidator.validate_date_range(
                    payload.start_month,
                    payload.start_year,
                    payload.end_month,
                    payload.end_year,
                )
                logger.info(f"Payload validation successful for user {userId}")
            except ValidationException as validation_error:
                logger.warning(
                    f"Experience payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "field": validation_error.field,
                        "code": validation_error.code,
                        "error": validation_error.message,
                    },
                )
                error_field = ValidationErrorField(
                    field=validation_error.field,
                    code=validation_error.code,
                    message=validation_error.message,
                    constraint=validation_error.constraint,
                )
                error_response = ValidationErrorResponse(
                    message="Please fix the validation errors below",
                    errors=[error_field],
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_response.model_dump(),
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
                priority=payload.priority,
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

    def list_experiences(self, db: Session, userId: str) -> list[ExperienceGetResponse]:
        """
        Retrieve all experiences for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch all experiences associated with user's profile
        5. Return experiences as response objects

        Args:
            db: Database session
            userId: Authenticated user's ID

        Returns:
            List of ExperienceGetResponse objects with experience details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(f"Starting experience retrieval process for user: {userId}")

            if not userId:
                logger.error(
                    "Experience retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Experience retrieval failed: User not found",
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
                    f"Experience retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(f"Fetching all experiences for profile: {user_profile.id}")

            experiences = (
                db.query(Experience)
                .filter(Experience.profileId == user_profile.id)
                .all()
            )

            logger.info(
                f"Successfully retrieved experiences",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceCount": len(experiences),
                },
            )

            return [
                ExperienceGetResponse.model_validate(experience)
                for experience in experiences
            ]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during experience retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving experiences.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during experience retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving experiences.",
            )

    def get_experience(
        self, db: Session, userId: str, experienceId: str
    ) -> ExperienceGetResponse:
        """
        Retrieve a specific experience by ID for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific experience by experienceId and profileId
        5. Verify experience exists and belongs to user's profile
        6. Return experience as response object

        Args:
            db: Database session
            userId: Authenticated user's ID
            experienceId: Experience ID to retrieve

        Returns:
            ExperienceGetResponse object with experience details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting experience retrieval process",
                extra={"userId": userId, "experienceId": experienceId},
            )

            if not userId:
                logger.error(
                    "Experience retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not experienceId:
                logger.error(
                    "Experience retrieval failed: No experience ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Experience ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Experience retrieval failed: User not found",
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
                    f"Experience retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching experience from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": experienceId,
                },
            )

            experience = (
                db.query(Experience)
                .filter(
                    Experience.profileId == user_profile.id,
                    Experience.id == experienceId,
                )
                .first()
            )

            if not experience:
                logger.warning(
                    f"Experience retrieval failed: Experience not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "experienceId": experienceId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Experience not found or does not belong to this user.",
                )

            logger.info(
                f"Successfully retrieved experience",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": experience.id,
                    "company": experience.company_name,
                    "role": experience.role,
                },
            )

            return ExperienceGetResponse.model_validate(experience)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during experience retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving experience.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during experience retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving experience.",
            )

    def update_experience(
        self,
        db: Session,
        userId: str,
        experienceId: str,
        payload: ExperienceUpdateRequest,
    ) -> ExperienceUpdateResponse:
        """
        Update an existing experience for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload (all fields are optional for partial updates)
        3. Verify user exists in database
        4. Verify user has a profile
        5. Fetch the specific experience by experienceId and profileId
        6. Verify experience exists and belongs to user's profile
        7. Update the experience fields
        8. Save changes and return updated experience

        Args:
            db: Database session
            userId: Authenticated user's ID
            experienceId: Experience ID to update
            payload: ExperienceUpdateRequest with fields to update (optional fields)

        Returns:
            ExperienceUpdateResponse object with updated experience details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting experience update process",
                extra={"userId": userId, "experienceId": experienceId},
            )

            if not userId:
                logger.error(
                    "Experience update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not experienceId:
                logger.error(
                    "Experience update failed: No experience ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Experience ID is required",
                )

            try:
                logger.info(f"Validating experience update payload for user {userId}")
                if payload.company_name is not None:
                    ExperienceValidator.validate_company_name(payload.company_name)
                if payload.role is not None:
                    ExperienceValidator.validate_role(payload.role)
                if payload.description is not None:
                    ExperienceValidator.validate_description(payload.description)
                if payload.techStack is not None:
                    ExperienceValidator.validate_tech_stack(payload.techStack)
                if payload.employment_type is not None:
                    ExperienceValidator.validate_employment_type(
                        payload.employment_type
                    )
                if payload.location_type is not None:
                    ExperienceValidator.validate_location_type(payload.location_type)
                if payload.location_details is not None:
                    ExperienceValidator.validate_location_details(
                        payload.location_details
                    )
                if payload.start_month is not None:
                    ExperienceValidator.validate_month(
                        payload.start_month, "start_month"
                    )
                if payload.start_year is not None:
                    ExperienceValidator.validate_year(payload.start_year, "start_year")
                if payload.end_month is not None:
                    ExperienceValidator.validate_month(payload.end_month, "end_month")
                if payload.end_year is not None:
                    ExperienceValidator.validate_year(payload.end_year, "end_year")
                if payload.priority is not None:
                    ExperienceValidator.validate_priority(payload.priority)
                if any(
                    [
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    ]
                ):
                    ExperienceValidator.validate_date_range(
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    )
                logger.info(f"Payload validation successful for user {userId}")
            except ValidationException as validation_error:
                logger.warning(
                    f"Experience payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "experienceId": experienceId,
                        "field": validation_error.field,
                        "code": validation_error.code,
                        "error": validation_error.message,
                    },
                )
                error_field = ValidationErrorField(
                    field=validation_error.field,
                    code=validation_error.code,
                    message=validation_error.message,
                    constraint=validation_error.constraint,
                )
                error_response = ValidationErrorResponse(
                    message="Please fix the validation errors below",
                    errors=[error_field],
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_response.model_dump(),
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Experience update failed: User not found",
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
                    f"Experience update failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching experience from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": experienceId,
                },
            )

            experience = (
                db.query(Experience)
                .filter(
                    Experience.profileId == user_profile.id,
                    Experience.id == experienceId,
                )
                .first()
            )

            if not experience:
                logger.warning(
                    f"Experience update failed: Experience not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "experienceId": experienceId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Experience not found or does not belong to this user.",
                )

            logger.info(f"Experience found, proceeding with update for {experienceId}")

            logger.info(f"Updating experience fields for {experienceId}")
            updated_fields = {}

            if payload.company_name is not None:
                experience.company_name = payload.company_name
                updated_fields["company_name"] = payload.company_name

            if payload.role is not None:
                experience.role = payload.role
                updated_fields["role"] = payload.role

            if payload.description is not None:
                experience.description = payload.description
                updated_fields["description"] = payload.description

            if payload.techStack is not None:
                experience.techStack = payload.techStack
                updated_fields["techStack"] = payload.techStack

            if payload.employment_type is not None:
                experience.employment_type = payload.employment_type
                updated_fields["employment_type"] = payload.employment_type

            if payload.location_type is not None:
                experience.location_type = payload.location_type
                updated_fields["location_type"] = payload.location_type

            if payload.location_details is not None:
                experience.location_details = payload.location_details
                updated_fields["location_details"] = payload.location_details

            if payload.start_month is not None:
                experience.start_month = payload.start_month
                updated_fields["start_month"] = payload.start_month

            if payload.start_year is not None:
                experience.start_year = payload.start_year
                updated_fields["start_year"] = payload.start_year

            if payload.end_month is not None:
                experience.end_month = payload.end_month
                updated_fields["end_month"] = payload.end_month

            if payload.end_year is not None:
                experience.end_year = payload.end_year
                updated_fields["end_year"] = payload.end_year

            if payload.priority is not None:
                experience.priority = payload.priority
                updated_fields["priority"] = payload.priority

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "experienceId": experienceId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving experience updates to database",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(experience)

            logger.info(
                f"Experience updated successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": experience.id,
                    "company": experience.company_name,
                    "role": experience.role,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return ExperienceUpdateResponse.model_validate(experience)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during experience update for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e.orig),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred during update.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during experience update for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating experience.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during experience update for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating experience.",
            )

    def delete_experience(self, db: Session, userId: str, experienceId: str) -> dict:
        """
        Delete a specific experience for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific experience by experienceId and profileId
        5. Verify experience exists and belongs to user's profile
        6. Delete the experience from database
        7. Return success response with deleted experience details

        Args:
            db: Database session
            userId: Authenticated user's ID
            experienceId: Experience ID to delete

        Returns:
            dict with success message and deleted experience ID

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting experience deletion process",
                extra={"userId": userId, "experienceId": experienceId},
            )

            if not userId:
                logger.error(
                    "Experience deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not experienceId:
                logger.error(
                    "Experience deletion failed: No experience ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Experience ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Experience deletion failed: User not found",
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
                    f"Experience deletion failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching experience from database for deletion",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": experienceId,
                },
            )

            experience = (
                db.query(Experience)
                .filter(
                    Experience.profileId == user_profile.id,
                    Experience.id == experienceId,
                )
                .first()
            )

            if not experience:
                logger.warning(
                    f"Experience deletion failed: Experience not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "experienceId": experienceId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Experience not found or does not belong to this user.",
                )

            deleted_experience_id = experience.id
            deleted_company = experience.company_name
            deleted_role = experience.role

            logger.info(
                f"Experience found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "experienceId": deleted_experience_id,
                    "company": deleted_company,
                    "role": deleted_role,
                },
            )

            logger.info(
                f"Deleting experience from database",
                extra={
                    "userId": userId,
                    "experienceId": deleted_experience_id,
                },
            )

            db.delete(experience)
            db.commit()

            logger.info(
                f"Experience deleted successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "experienceId": deleted_experience_id,
                    "company": deleted_company,
                    "role": deleted_role,
                },
            )

            return {
                "success": True,
                "message": "Experience deleted successfully",
                "deletedExperienceId": str(deleted_experience_id),
                "company": deleted_company,
                "role": deleted_role,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during experience deletion for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting experience.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during experience deletion for user {userId}",
                extra={
                    "userId": userId,
                    "experienceId": experienceId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting experience.",
            )
