from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.Profile import Profile
from app.models.User import User
from app.models.Achievement import Achievement
from app.schema.Achievement import AchievementCreateRequest, AchievementUpdateRequest
from app.response.achievement_responses import (
    AchievementCreateResponse,
    AchievementGetResponse,
    AchievementUpdateResponse,
)
from app.core.logger import logger
from app.validators.achievement_validators import AchievementValidator
from app.helpers.db_helpers import get_user_profile


class AchievementServiceClass:
    async def create_achievement(
        self, db: Session, payload: AchievementCreateRequest, userId
    ) -> AchievementCreateResponse:
        """
        Create a new achievement record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Verify user has a profile
        5. Create and save the achievement record

        Args:
            db: Database session
            payload: AchievementCreateRequest with achievement details
            userId: Authenticated user's ID

        Returns:
            AchievementCreateResponse with created achievement details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting achievement creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Achievement creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(
                    f"Validating achievement creation payload for user {userId}"
                )
                AchievementValidator.validate_title(payload.title)
                AchievementValidator.validate_achievement_type(payload.achievement_type)
                AchievementValidator.validate_description(payload.description)
                AchievementValidator.validate_location(payload.location)
                AchievementValidator.validate_month(payload.start_month)
                AchievementValidator.validate_year(payload.start_year)
                AchievementValidator.validate_month(payload.end_month)
                AchievementValidator.validate_year(payload.end_year)
                AchievementValidator.validate_links(payload.links)
                AchievementValidator.validate_date_range(
                    payload.start_month,
                    payload.start_year,
                    payload.end_month,
                    payload.end_year,
                )
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Achievement payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "error": str(validation_error),
                        "title": payload.title,
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
                    f"Achievement creation failed: User not found",
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
                f"Creating achievement record for user {userId} with title: {payload.title}"
            )

            achievement = Achievement(
                title=payload.title,
                achievement_type=payload.achievement_type,
                description=payload.description,
                location=payload.location,
                start_month=payload.start_month,
                start_year=payload.start_year,
                end_month=payload.end_month,
                end_year=payload.end_year,
                links=payload.links,
                profileId=user_profile.id,
            )

            db.add(achievement)
            db.commit()
            db.refresh(achievement)

            logger.info(
                f"Achievement record created successfully",
                extra={
                    "userId": userId,
                    "achievementId": achievement.id,
                    "title": achievement.title,
                    "type": achievement.achievement_type,
                },
            )

            return AchievementCreateResponse.model_validate(achievement)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during achievement creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "title": payload.title if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This achievement record may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during achievement creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating achievement record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during achievement creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the achievement record.",
            )

    async def list_achievements(
        self, db: Session, userId: str
    ) -> list[AchievementGetResponse]:
        """
        Retrieve all achievement records for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch all achievement records associated with user's profile
        5. Return achievement records as response objects

        Args:
            db: Database session
            userId: Authenticated user's ID

        Returns:
            List of AchievementGetResponse objects with achievement details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(f"Starting achievement retrieval process for user: {userId}")

            if not userId:
                logger.error(
                    "Achievement retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Achievement retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            if not user_profile:
                logger.warning(
                    f"Achievement retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching all achievement records for profile: {user_profile.id}"
            )

            achievements = (
                db.query(Achievement)
                .filter(Achievement.profileId == user_profile.id)
                .all()
            )

            logger.info(
                f"Successfully retrieved achievement records",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementCount": len(achievements),
                },
            )

            return [
                AchievementGetResponse.model_validate(achievement)
                for achievement in achievements
            ]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during achievement retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving achievement records.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during achievement retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving achievement records.",
            )

    async def get_achievement(
        self, db: Session, userId: str, achievementId: str
    ) -> AchievementGetResponse:
        """
        Retrieve a specific achievement record by ID for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific achievement record by achievementId and profileId
        5. Verify achievement record exists and belongs to user's profile
        6. Return achievement record as response object

        Args:
            db: Database session
            userId: Authenticated user's ID
            achievementId: Achievement record ID to retrieve

        Returns:
            AchievementGetResponse object with achievement details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting achievement retrieval process",
                extra={"userId": userId, "achievementId": achievementId},
            )

            if not userId:
                logger.error(
                    "Achievement retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not achievementId:
                logger.error(
                    "Achievement retrieval failed: No achievement ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Achievement ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Achievement retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            if not user_profile:
                logger.warning(
                    f"Achievement retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching achievement record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": achievementId,
                },
            )

            achievement = (
                db.query(Achievement)
                .filter(
                    Achievement.profileId == user_profile.id,
                    Achievement.id == achievementId,
                )
                .first()
            )

            if not achievement:
                logger.warning(
                    f"Achievement retrieval failed: Achievement record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "achievementId": achievementId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Achievement record not found or does not belong to this user.",
                )

            logger.info(
                f"Successfully retrieved achievement record",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": achievement.id,
                    "title": achievement.title,
                    "type": achievement.achievement_type,
                },
            )

            return AchievementGetResponse.model_validate(achievement)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during achievement retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving achievement record.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during achievement retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving achievement record.",
            )

    async def update_achievement(
        self,
        db: Session,
        userId: str,
        achievementId: str,
        payload: AchievementUpdateRequest,
    ) -> AchievementUpdateResponse:
        """
        Update an existing achievement record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload (all fields are optional for partial updates)
        3. Verify user exists in database
        4. Verify user has a profile
        5. Fetch the specific achievement record by achievementId and profileId
        6. Verify achievement record exists and belongs to user's profile
        7. Update the achievement record fields
        8. Save changes and return updated achievement record

        Args:
            db: Database session
            userId: Authenticated user's ID
            achievementId: Achievement record ID to update
            payload: AchievementUpdateRequest with fields to update (optional fields)

        Returns:
            AchievementUpdateResponse object with updated achievement details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting achievement update process",
                extra={"userId": userId, "achievementId": achievementId},
            )

            if not userId:
                logger.error(
                    "Achievement update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not achievementId:
                logger.error(
                    "Achievement update failed: No achievement ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Achievement ID is required",
                )

            try:
                logger.info(f"Validating achievement update payload for user {userId}")
                if payload.title is not None:
                    AchievementValidator.validate_title(payload.title)
                if payload.achievement_type is not None:
                    AchievementValidator.validate_achievement_type(
                        payload.achievement_type
                    )
                if payload.description is not None:
                    AchievementValidator.validate_description(payload.description)
                if payload.location is not None:
                    AchievementValidator.validate_location(payload.location)
                if payload.start_month is not None:
                    AchievementValidator.validate_month(payload.start_month)
                if payload.start_year is not None:
                    AchievementValidator.validate_year(payload.start_year)
                if payload.end_month is not None:
                    AchievementValidator.validate_month(payload.end_month)
                if payload.end_year is not None:
                    AchievementValidator.validate_year(payload.end_year)
                if payload.links is not None:
                    AchievementValidator.validate_links(payload.links)
                if any(
                    [
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    ]
                ):
                    AchievementValidator.validate_date_range(
                        payload.start_month,
                        payload.start_year,
                        payload.end_month,
                        payload.end_year,
                    )
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Achievement payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "achievementId": achievementId,
                        "error": str(validation_error),
                        "title": payload.title,
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
                    f"Achievement update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            if not user_profile:
                logger.warning(
                    f"Achievement update failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching achievement record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": achievementId,
                },
            )

            achievement = (
                db.query(Achievement)
                .filter(
                    Achievement.profileId == user_profile.id,
                    Achievement.id == achievementId,
                )
                .first()
            )

            if not achievement:
                logger.warning(
                    f"Achievement update failed: Achievement record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "achievementId": achievementId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Achievement record not found or does not belong to this user.",
                )

            logger.info(
                f"Achievement record found, proceeding with update for {achievementId}"
            )

            logger.info(f"Updating achievement record fields for {achievementId}")
            updated_fields = {}

            if payload.title is not None:
                achievement.title = payload.title
                updated_fields["title"] = payload.title

            if payload.achievement_type is not None:
                achievement.achievement_type = payload.achievement_type
                updated_fields["achievement_type"] = payload.achievement_type

            if payload.description is not None:
                achievement.description = payload.description
                updated_fields["description"] = payload.description

            if payload.location is not None:
                achievement.location = payload.location
                updated_fields["location"] = payload.location

            if payload.start_month is not None:
                achievement.start_month = payload.start_month
                updated_fields["start_month"] = payload.start_month

            if payload.start_year is not None:
                achievement.start_year = payload.start_year
                updated_fields["start_year"] = payload.start_year

            if payload.end_month is not None:
                achievement.end_month = payload.end_month
                updated_fields["end_month"] = payload.end_month

            if payload.end_year is not None:
                achievement.end_year = payload.end_year
                updated_fields["end_year"] = payload.end_year

            if payload.links is not None:
                achievement.links = payload.links
                updated_fields["links"] = payload.links

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "achievementId": achievementId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving achievement record updates to database",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(achievement)

            logger.info(
                f"Achievement record updated successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": achievement.id,
                    "title": achievement.title,
                    "type": achievement.achievement_type,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return AchievementUpdateResponse.model_validate(achievement)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during achievement update for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
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
                f"Database error during achievement update for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating achievement record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during achievement update for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating achievement record.",
            )

    async def delete_achievement(
        self, db: Session, userId: str, achievementId: str
    ) -> dict:
        """
        Delete a specific achievement record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific achievement record by achievementId and profileId
        5. Verify achievement record exists and belongs to user's profile
        6. Delete the achievement record from database
        7. Return success response with deleted achievement record details

        Args:
            db: Database session
            userId: Authenticated user's ID
            achievementId: Achievement record ID to delete

        Returns:
            dict with success message and deleted achievement record ID

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting achievement deletion process",
                extra={"userId": userId, "achievementId": achievementId},
            )

            if not userId:
                logger.error(
                    "Achievement deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not achievementId:
                logger.error(
                    "Achievement deletion failed: No achievement ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Achievement ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Achievement deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = await get_user_profile(db, userId)

            if not user_profile:
                logger.warning(
                    f"Achievement deletion failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist.",
                )

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching achievement record from database for deletion",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": achievementId,
                },
            )

            achievement = (
                db.query(Achievement)
                .filter(
                    Achievement.profileId == user_profile.id,
                    Achievement.id == achievementId,
                )
                .first()
            )

            if not achievement:
                logger.warning(
                    f"Achievement deletion failed: Achievement record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "achievementId": achievementId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Achievement record not found or does not belong to this user.",
                )

            deleted_achievement_id = achievement.id
            deleted_title = achievement.title
            deleted_type = achievement.achievement_type

            logger.info(
                f"Achievement record found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "achievementId": deleted_achievement_id,
                    "title": deleted_title,
                    "type": deleted_type,
                },
            )

            logger.info(
                f"Deleting achievement record from database",
                extra={
                    "userId": userId,
                    "achievementId": deleted_achievement_id,
                },
            )

            db.delete(achievement)
            db.commit()

            logger.info(
                f"Achievement record deleted successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "achievementId": deleted_achievement_id,
                    "title": deleted_title,
                    "type": deleted_type,
                },
            )

            return {
                "success": True,
                "message": "Achievement record deleted successfully",
                "deletedAchievementId": str(deleted_achievement_id),
                "title": deleted_title,
                "type": deleted_type,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during achievement deletion for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting achievement record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during achievement deletion for user {userId}",
                extra={
                    "userId": userId,
                    "achievementId": achievementId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting achievement record.",
            )
