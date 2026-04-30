from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.Profile import Profile
from app.models.User import User
from app.models.Publication import Publication
from app.schema.Publication import PublicationCreateRequest, PublicationUpdateRequest
from app.response.publication_responses import (
    PublicationCreateResponse,
    PublicationGetResponse,
    PublicationUpdateResponse,
)
from app.core.logger import logger
from app.validators.publication_validators import PublicationValidator
from app.helpers.db_helpers import get_user_profile


class PublicationServiceClass:
    def create_publication(
        self, db: Session, payload: PublicationCreateRequest, userId
    ) -> PublicationCreateResponse:
        """
        Create a new publication record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Verify user has a profile
        5. Create and save the publication record

        Args:
            db: Database session
            payload: PublicationCreateRequest with publication details
            userId: Authenticated user's ID

        Returns:
            PublicationCreateResponse with created publication details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting publication creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Publication creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(
                    f"Validating publication creation payload for user {userId}"
                )
                PublicationValidator.validate_title(payload.title)
                PublicationValidator.validate_publisher(payload.publisher)
                PublicationValidator.validate_publication_date(payload.publication_date)
                PublicationValidator.validate_authors(payload.authors)
                PublicationValidator.validate_description(payload.description)
                PublicationValidator.validate_url(payload.url)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Publication payload validation failed for user {userId}",
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
                    f"Publication creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = get_user_profile(db, userId).first()

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Creating publication record for user {userId} with title: {payload.title}"
            )

            publication = Publication(
                title=payload.title,
                publisher=payload.publisher,
                publication_date=payload.publication_date,
                authors=payload.authors,
                description=payload.description,
                url=payload.url,
                profileId=user_profile.id,
            )

            db.add(publication)
            db.commit()
            db.refresh(publication)

            logger.info(
                f"Publication record created successfully",
                extra={
                    "userId": userId,
                    "publicationId": publication.id,
                    "title": publication.title,
                    "publisher": publication.publisher,
                },
            )

            return PublicationCreateResponse.model_validate(publication)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during publication creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "title": payload.title if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This publication record may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during publication creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating publication record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during publication creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the publication record.",
            )

    def list_publications(
        self, db: Session, userId: str
    ) -> list[PublicationGetResponse]:
        """
        Retrieve all publication records for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch all publication records associated with user's profile
        5. Return publication records as response objects

        Args:
            db: Database session
            userId: Authenticated user's ID

        Returns:
            List of PublicationGetResponse objects with publication details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(f"Starting publication retrieval process for user: {userId}")

            if not userId:
                logger.error(
                    "Publication retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Publication retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = get_user_profile(db, userId).first()

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching all publication records for profile: {user_profile.id}"
            )

            publications = (
                db.query(Publication)
                .filter(Publication.profileId == user_profile.id)
                .all()
            )

            logger.info(
                f"Successfully retrieved publication records",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationCount": len(publications),
                },
            )

            return [
                PublicationGetResponse.model_validate(publication)
                for publication in publications
            ]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during publication retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving publication records.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during publication retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving publication records.",
            )

    def get_publication(
        self, db: Session, userId: str, publicationId: str
    ) -> PublicationGetResponse:
        """
        Retrieve a specific publication record by ID for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific publication record by publicationId and profileId
        5. Verify publication record exists and belongs to user's profile
        6. Return publication record as response object

        Args:
            db: Database session
            userId: Authenticated user's ID
            publicationId: Publication record ID to retrieve

        Returns:
            PublicationGetResponse object with publication details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting publication retrieval process",
                extra={"userId": userId, "publicationId": publicationId},
            )

            if not userId:
                logger.error(
                    "Publication retrieval failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not publicationId:
                logger.error(
                    "Publication retrieval failed: No publication ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Publication ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Publication retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = get_user_profile(db, userId).first()

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching publication record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": publicationId,
                },
            )

            publication = (
                db.query(Publication)
                .filter(
                    Publication.profileId == user_profile.id,
                    Publication.id == publicationId,
                )
                .first()
            )

            if not publication:
                logger.warning(
                    f"Publication retrieval failed: Publication record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "publicationId": publicationId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Publication record not found or does not belong to this user.",
                )

            logger.info(
                f"Successfully retrieved publication record",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": publication.id,
                    "title": publication.title,
                    "publisher": publication.publisher,
                },
            )

            return PublicationGetResponse.model_validate(publication)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during publication retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving publication record.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during publication retrieval for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving publication record.",
            )

    def update_publication(
        self,
        db: Session,
        userId: str,
        publicationId: str,
        payload: PublicationUpdateRequest,
    ) -> PublicationUpdateResponse:
        """
        Update an existing publication record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload (all fields are optional for partial updates)
        3. Verify user exists in database
        4. Verify user has a profile
        5. Fetch the specific publication record by publicationId and profileId
        6. Verify publication record exists and belongs to user's profile
        7. Update the publication record fields
        8. Save changes and return updated publication record

        Args:
            db: Database session
            userId: Authenticated user's ID
            publicationId: Publication record ID to update
            payload: PublicationUpdateRequest with fields to update (optional fields)

        Returns:
            PublicationUpdateResponse object with updated publication details

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting publication update process",
                extra={"userId": userId, "publicationId": publicationId},
            )

            if not userId:
                logger.error(
                    "Publication update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not publicationId:
                logger.error(
                    "Publication update failed: No publication ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Publication ID is required",
                )

            try:
                logger.info(f"Validating publication update payload for user {userId}")
                if payload.title is not None:
                    PublicationValidator.validate_title(payload.title)
                if payload.publisher is not None:
                    PublicationValidator.validate_publisher(payload.publisher)
                if payload.publication_date is not None:
                    PublicationValidator.validate_publication_date(
                        payload.publication_date
                    )
                if payload.authors is not None:
                    PublicationValidator.validate_authors(payload.authors)
                if payload.description is not None:
                    PublicationValidator.validate_description(payload.description)
                if payload.url is not None:
                    PublicationValidator.validate_url(payload.url)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Publication payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "publicationId": publicationId,
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
                    f"Publication update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = get_user_profile(db, userId).first()

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching publication record from database",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": publicationId,
                },
            )

            publication = (
                db.query(Publication)
                .filter(
                    Publication.profileId == user_profile.id,
                    Publication.id == publicationId,
                )
                .first()
            )

            if not publication:
                logger.warning(
                    f"Publication update failed: Publication record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "publicationId": publicationId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Publication record not found or does not belong to this user.",
                )

            logger.info(
                f"Publication record found, proceeding with update for {publicationId}"
            )

            logger.info(f"Updating publication record fields for {publicationId}")
            updated_fields = {}

            if payload.title is not None:
                publication.title = payload.title
                updated_fields["title"] = payload.title

            if payload.publisher is not None:
                publication.publisher = payload.publisher
                updated_fields["publisher"] = payload.publisher

            if payload.publication_date is not None:
                publication.publication_date = payload.publication_date
                updated_fields["publication_date"] = payload.publication_date

            if payload.authors is not None:
                publication.authors = payload.authors
                updated_fields["authors"] = payload.authors

            if payload.description is not None:
                publication.description = payload.description
                updated_fields["description"] = payload.description

            if payload.url is not None:
                publication.url = payload.url
                updated_fields["url"] = payload.url

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "publicationId": publicationId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving publication record updates to database",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(publication)

            logger.info(
                f"Publication record updated successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": publication.id,
                    "title": publication.title,
                    "publisher": publication.publisher,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return PublicationUpdateResponse.model_validate(publication)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during publication update for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
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
                f"Database error during publication update for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating publication record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during publication update for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating publication record.",
            )

    def delete_publication(self, db: Session, userId: str, publicationId: str) -> dict:
        """
        Delete a specific publication record for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify user has a profile
        4. Fetch the specific publication record by publicationId and profileId
        5. Verify publication record exists and belongs to user's profile
        6. Delete the publication record from database
        7. Return success response with deleted publication record details

        Args:
            db: Database session
            userId: Authenticated user's ID
            publicationId: Publication record ID to delete

        Returns:
            dict with success message and deleted publication record ID

        Raises:
            HTTPException: For authentication, validation, or database errors
        """
        try:
            logger.info(
                f"Starting publication deletion process",
                extra={"userId": userId, "publicationId": publicationId},
            )

            if not userId:
                logger.error(
                    "Publication deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not publicationId:
                logger.error(
                    "Publication deletion failed: No publication ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Publication ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Publication deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying user profile exists for user: {userId}")
            user_profile = get_user_profile(db, userId).first()

            logger.info(f"User profile verified successfully for user: {userId}")

            logger.info(
                f"Fetching publication record from database for deletion",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": publicationId,
                },
            )

            publication = (
                db.query(Publication)
                .filter(
                    Publication.profileId == user_profile.id,
                    Publication.id == publicationId,
                )
                .first()
            )

            if not publication:
                logger.warning(
                    f"Publication deletion failed: Publication record not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "profileId": user_profile.id,
                        "publicationId": publicationId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Publication record not found or does not belong to this user.",
                )

            deleted_publication_id = publication.id
            deleted_title = publication.title
            deleted_publisher = publication.publisher

            logger.info(
                f"Publication record found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "publicationId": deleted_publication_id,
                    "title": deleted_title,
                    "publisher": deleted_publisher,
                },
            )

            logger.info(
                f"Deleting publication record from database",
                extra={
                    "userId": userId,
                    "publicationId": deleted_publication_id,
                },
            )

            db.delete(publication)
            db.commit()

            logger.info(
                f"Publication record deleted successfully",
                extra={
                    "userId": userId,
                    "profileId": user_profile.id,
                    "publicationId": deleted_publication_id,
                    "title": deleted_title,
                    "publisher": deleted_publisher,
                },
            )

            return {
                "success": True,
                "message": "Publication record deleted successfully",
                "deletedPublicationId": str(deleted_publication_id),
                "title": deleted_title,
                "publisher": deleted_publisher,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during publication deletion for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting publication record.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during publication deletion for user {userId}",
                extra={
                    "userId": userId,
                    "publicationId": publicationId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting publication record.",
            )
