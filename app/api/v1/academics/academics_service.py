from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.Profile import Profile
from app.models.User import User
from app.models.Academic import Academic
from app.schema.Academic import AcademicCreateRequest, AcademicUpdateRequest
from app.response.academic_responses import (
    AcademicCreateResponse,
    AcademicGetResponse,
    AcademicUpdateResponse,
)
from app.core.logger import logger
from app.validators.academic_validators import AcademicValidator
from app.helpers.db_helpers import get_user_profile


class AcademicServiceClass:
    async def create_academic(
        self, db: Session, payload: AcademicCreateRequest, userId
    ) -> AcademicCreateResponse:
        """
        Create a new academic record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Verify user has a profile
        5. Create and save the academic record

        Args:
            db: Database session
            payload: AcademicCreateRequest with academic details
            userId: Authenticated user's ID

        Returns:
            AcademicCreateResponse with created academic details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting academic creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Academic creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(f"Validating academic creation payload for user {userId}")
                AcademicValidator.validate_degree_name(payload.degree_name)
                AcademicValidator.validate_college_name(payload.college_name)
                AcademicValidator.validate_description(payload.description)
                AcademicValidator.validate_links(payload.links)
                AcademicValidator.validate_month(payload.start_month)
                AcademicValidator.validate_year(payload.start_year)
                AcademicValidator.validate_month(payload.end_month)
                AcademicValidator.validate_year(payload.end_year)
                AcademicValidator.validate_date_range(
                    payload.start_month,
                    payload.start_year,
                    payload.end_month,
                    payload.end_year,
                )
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Academic payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "error": str(validation_error),
                        "degreeName": payload.degree_name,
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
                    f"Academic creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Creating academic record for user {userId} with degree: {payload.degree_name}"
            )

            academic = Academic(
                degree_name=payload.degree_name,
                college_name=payload.college_name,
                description=payload.description,
                links=payload.links,
                start_month=payload.start_month,
                start_year=payload.start_year,
                end_month=payload.end_month,
                end_year=payload.end_year,
                profileId=user_profile.id,
            )

            db.add(academic)
            db.commit()
            db.refresh(academic)

            logger.info(
                f"Academic record created successfully",
                extra={
                    "userId": userId,
                    "academicId": academic.id,
                    "degree": academic.degree_name,
                    "college": academic.college_name,
                },
            )

            return AcademicCreateResponse.model_validate(academic)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during academic creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "degree": payload.degree_name if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This academic record may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during academic creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating academic record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during academic creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the academic record.",
            )

    async def list_academics(
        self, db: Session, userId: str
    ) -> list[AcademicGetResponse]:
        """
        Retrieve all academic records for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch all academic records associated with user's profile
        5. Return academic records as response objects

        Args:
            db: Database session
            userId: Authenticated user's ID

        Returns:
            List of AcademicGetResponse objects with academic details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(f"Starting academic retrieval process for user: {userId}")

            if not userId:
                logger.error(
                    "Academic retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Academic retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(f"Fetching all academic records for profile: {user_profile.id}")

            academics = (
                db.query(Academic).filter(Academic.profileId == user_profile.id).all()
            )

            logger.info(
                f"Successfully retrieved academic records",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicCount": len(academics),
                },
            )

            return [
                AcademicGetResponse.model_validate(academic) for academic in academics
            ]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during academic retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving academic records.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during academic retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving academic records.",
            )

    async def get_academic(
        self, db: Session, userId: str, academicId: str
    ) -> AcademicGetResponse:
        """
        Retrieve a specific academic record by ID for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific academic record by academicId and profileId
        5. Verify academic record exists and belongs to user's profile
        6. Return academic record as response object

        Args:
            db: Database session
            userId: Authenticated user's ID
            academicId: Academic record ID to retrieve

        Returns:
            AcademicGetResponse object with academic details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting academic retrieval process",
                extra={"userId": userId, "academicId": academicId},
            )

            if not userId:
                logger.error(
                    "Academic retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not academicId:
                logger.error(
                    "Academic retrieval failed: No academic ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Academic ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Academic retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching academic record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": academicId,
                },
            )

            academic = (
                db.query(Academic)
                .filter(
                    Academic.profileId == user_profile.id,
                    Academic.id == academicId,
                )
                .first()
            )

            if not academic:
                logger.warning(
                    f"Academic retrieval failed: Academic record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "academicId": academicId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Academic record not found or does not belong to this user.",
                )

            logger.info(
                f"Successfully retrieved academic record",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": academic.id,
                    "degree": academic.degree_name,
                    "college": academic.college_name,
                },
            )

            return AcademicGetResponse.model_validate(academic)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during academic retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving academic record.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during academic retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving academic record.",
            )

    async def update_academic(
        self,
        db: Session,
        userId: str,
        academicId: str,
        payload: AcademicUpdateRequest,
    ) -> AcademicUpdateResponse:
        """
        Update an existing academic record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload (all fields are optional for partial updates)
        3. Verify user exists in database
        4. Verify user has a profile
        5. Fetch the specific academic record by academicId and profileId
        6. Verify academic record exists and belongs to user's profile
        7. Update the academic record fields
        8. Save changes and return updated academic record

        Args:
            db: Database session
            userId: Authenticated user's ID
            academicId: Academic record ID to update
            payload: AcademicUpdateRequest with fields to update (optional fields)

        Returns:
            AcademicUpdateResponse object with updated academic details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting academic update process",
                extra={"userId": userId, "academicId": academicId},
            )

            if not userId:
                logger.error(
                    "Academic update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not academicId:
                logger.error(
                    "Academic update failed: No academic ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Academic ID is required",
                )

            try:
                logger.info(f"Validating academic update payload for user {userId}")
                if payload.degree_name is not None:
                    AcademicValidator.validate_degree_name(payload.degree_name)
                if payload.college_name is not None:
                    AcademicValidator.validate_college_name(payload.college_name)
                if payload.description is not None:
                    AcademicValidator.validate_description(payload.description)
                if payload.links is not None:
                    AcademicValidator.validate_links(payload.links)
                if payload.start_month is not None:
                    AcademicValidator.validate_month(payload.start_month)
                if payload.start_year is not None:
                    AcademicValidator.validate_year(payload.start_year)
                if payload.end_month is not None:
                    AcademicValidator.validate_month(payload.end_month)
                if payload.end_year is not None:
                    AcademicValidator.validate_year(payload.end_year)
                if any(
                    [
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    ]
                ):
                    AcademicValidator.validate_date_range(
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    )
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Academic payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "academicId": academicId,
                        "error": str(validation_error),
                        "degree": payload.degree_name,
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
                    f"Academic update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching academic record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": academicId,
                },
            )

            academic = (
                db.query(Academic)
                .filter(
                    Academic.profileId == user_profile.id,
                    Academic.id == academicId,
                )
                .first()
            )

            if not academic:
                logger.warning(
                    f"Academic update failed: Academic record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "academicId": academicId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Academic record not found or does not belong to this user.",
                )

            logger.info(
                f"Academic record found, proceeding with update for {academicId}"
            )

            logger.info(f"Updating academic record fields for {academicId}")
            updated_fields = {}

            if payload.degree_name is not None:
                academic.degree_name = payload.degree_name
                updated_fields["degree_name"] = payload.degree_name

            if payload.college_name is not None:
                academic.college_name = payload.college_name
                updated_fields["college_name"] = payload.college_name

            if payload.description is not None:
                academic.description = payload.description
                updated_fields["description"] = payload.description

            if payload.links is not None:
                academic.links = payload.links
                updated_fields["links"] = payload.links

            if payload.start_month is not None:
                academic.start_month = payload.start_month
                updated_fields["start_month"] = payload.start_month

            if payload.start_year is not None:
                academic.start_year = payload.start_year
                updated_fields["start_year"] = payload.start_year

            if payload.end_month is not None:
                academic.end_month = payload.end_month
                updated_fields["end_month"] = payload.end_month

            if payload.end_year is not None:
                academic.end_year = payload.end_year
                updated_fields["end_year"] = payload.end_year

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "academicId": academicId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving academic record updates to database",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(academic)

            logger.info(
                f"Academic record updated successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": academic.id,
                    "degree": academic.degree_name,
                    "college": academic.college_name,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return AcademicUpdateResponse.model_validate(academic)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during academic update for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
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
                f"Database error during academic update for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating academic record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during academic update for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating academic record.",
            )

    async def delete_academic(self, db: Session, userId: str, academicId: str) -> dict:
        """
        Delete a specific academic record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific academic record by academicId and profileId
        5. Verify academic record exists and belongs to user's profile
        6. Delete the academic record from database
        7. Return success response with deleted academic record details

        Args:
            db: Database session
            userId: Authenticated user's ID
            academicId: Academic record ID to delete

        Returns:
            dict with success message and deleted academic record ID

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting academic deletion process",
                extra={"userId": userId, "academicId": academicId},
            )

            if not userId:
                logger.error(
                    "Academic deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not academicId:
                logger.error(
                    "Academic deletion failed: No academic ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Academic ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Academic deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")

            user_profile = await get_user_profile(db, userId)

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching academic record from database for deletion",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": academicId,
                },
            )

            academic = (
                db.query(Academic)
                .filter(
                    Academic.profileId == user_profile.id,
                    Academic.id == academicId,
                )
                .first()
            )

            if not academic:
                logger.warning(
                    f"Academic deletion failed: Academic record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "academicId": academicId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Academic record not found or does not belong to this user.",
                )

            deleted_academic_id = academic.id
            deleted_degree = academic.degree_name
            deleted_college = academic.college_name

            logger.info(
                f"Academic record found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "academicId": deleted_academic_id,
                    "degree": deleted_degree,
                    "college": deleted_college,
                },
            )

            logger.info(
                f"Deleting academic record from database",
                extra={
                    "userId": userId,
                    "academicId": deleted_academic_id,
                },
            )

            db.delete(academic)
            db.commit()

            logger.info(
                f"Academic record deleted successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "academicId": deleted_academic_id,
                    "degree": deleted_degree,
                    "college": deleted_college,
                },
            )

            return {
                "success": True,
                "message": "Academic record deleted successfully",
                "deletedAcademicId": str(deleted_academic_id),
                "degree": deleted_degree,
                "college": deleted_college,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during academic deletion for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting academic record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during academic deletion for user {userId}",
                extra={
                    "userId": userId,
                    "academicId": academicId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting academic record.",
            )
