from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from pydantic import ValidationError
from app.models.Profile import Profile
from app.models.User import User
from app.schema.Profile import (
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.response.profile_responses import (
    ProfileCreateResponse,
    ProfileGetResponse,
    ProfileUpdateResponse,
)
from app.core.logger import logger
from app.validators.profile_validators import ProfileValidator


class ProfileServiceClass:

    def create_profile(
        self, db: Session, payload: ProfileCreateRequest, userId: str
    ) -> ProfileCreateResponse:
        """
        Create a new profile for a user.

        Args:
            db: Database session
            payload: Profile creation request data
            userId: User ID who owns the profile

        Returns:
            ProfileCreateResponse: Created profile data

        Raises:
            HTTPException: If validation fails, user not found, or profile already exists
        """
        try:
            if not userId:
                logger.error(
                    f"Profile creation failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            try:
                logger.info(f"Validating profile creation request for user: {userId}")
                ProfileValidator.validate_full_name(payload.full_name)
                ProfileValidator.validate_headline(payload.headline)
                ProfileValidator.validate_summary(payload.summary)
                ProfileValidator.validate_links(payload.links)
            except ValueError as validation_error:
                logger.warning(
                    f"Profile validation failed for user {userId}: {str(validation_error)}",
                    extra={"userId": userId, "error": str(validation_error)},
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Profile creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile already exists for user: {userId}")
            existing_profile = (
                db.query(Profile).filter(Profile.userId == user.id).first()
            )

            if existing_profile:
                logger.warning(
                    f"Profile creation failed: User already has a profile",
                    extra={"userId": userId, "profileId": str(existing_profile.id)},
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already has a profile. Update the existing profile instead.",
                )

            logger.info(
                f"Creating new profile for user: {userId}",
                extra={"userId": userId},
            )
            profile = Profile(
                userId=user.id,
                full_name=payload.full_name,
                summary=payload.summary,
                headline=payload.headline,
                links=payload.links,
            )

            db.add(profile)
            db.commit()
            db.refresh(profile)

            logger.info(
                f"Profile created successfully for user: {userId}",
                extra={"userId": userId, "profileId": str(profile.id)},
            )

            return ProfileCreateResponse.model_validate(profile)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during profile creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating profile",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during profile creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating profile",
            )

    def get_profile(self, db: Session, userId: str) -> ProfileGetResponse:
        """
        Get profile details for a user.

        Args:
            db: Database session
            userId: User ID whose profile to retrieve

        Returns:
            ProfileGetResponse: User profile data

        Raises:
            HTTPException: If user not found or profile doesn't exist
        """
        try:
            if not userId:
                logger.error(
                    f"Profile retrieval failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Profile retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Retrieving profile for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Profile retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(
                f"Profile retrieved successfully for user: {userId}",
                extra={"userId": userId, "profileId": str(user_profile.id)},
            )

            return ProfileGetResponse.model_validate(user_profile)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during profile retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving profile",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during profile retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving profile",
            )

    def update_profile(
        self, db: Session, userId: str, payload: ProfileUpdateRequest
    ) -> ProfileUpdateResponse:
        """
        Update an existing user profile.

        Args:
            db: Database session
            userId: User ID whose profile to update
            payload: Profile update request data

        Returns:
            ProfileUpdateResponse: Updated profile data

        Raises:
            HTTPException: If validation fails, user not found, or profile doesn't exist
        """
        try:
            if not userId:
                logger.error(
                    f"Profile update failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            try:
                logger.info(f"Validating profile update request for user: {userId}")
                if payload.full_name is not None:
                    ProfileValidator.validate_full_name(payload.full_name)
                if payload.headline is not None:
                    ProfileValidator.validate_headline(payload.headline)
                if payload.summary is not None:
                    ProfileValidator.validate_summary(payload.summary)
                if payload.links is not None:
                    ProfileValidator.validate_links(payload.links)
            except ValueError as validation_error:
                logger.warning(
                    f"Profile update validation failed for user {userId}: {str(validation_error)}",
                    extra={"userId": userId, "error": str(validation_error)},
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Profile update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Retrieving profile for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Profile update failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first.",
                )

            logger.info(
                f"Updating profile for user: {userId}",
                extra={"userId": userId, "profileId": str(user_profile.id)},
            )

            if payload.full_name is not None:
                user_profile.full_name = payload.full_name
                logger.debug(
                    f"Updated full_name for user {userId}",
                    extra={"userId": userId, "full_name": payload.full_name},
                )

            if payload.headline is not None:
                user_profile.headline = payload.headline
                logger.debug(
                    f"Updated headline for user {userId}",
                    extra={"userId": userId, "headline": payload.headline},
                )

            if payload.summary is not None:
                user_profile.summary = payload.summary
                logger.debug(
                    f"Updated summary for user {userId}",
                    extra={"userId": userId},
                )

            if payload.links is not None:
                user_profile.links = payload.links
                logger.debug(
                    f"Updated links for user {userId}",
                    extra={"userId": userId},
                )

            db.commit()
            db.refresh(user_profile)

            logger.info(
                f"Profile updated successfully for user: {userId}",
                extra={"userId": userId, "profileId": str(user_profile.id)},
            )

            return ProfileUpdateResponse.model_validate(user_profile)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during profile update for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating profile",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during profile update for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating profile",
            )
