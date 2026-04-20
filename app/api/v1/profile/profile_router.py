from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
)
from app.response.profile_responses import (
    ProfileCreateResponse,
    ProfileGetResponse,
    ProfileUpdateResponse,
    ProfileDeleteResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .profile_service import ProfileServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.post(
    "/",
    response_model=ProfileCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    data: ProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user profile.

    Args:
        data: Profile creation request data (full_name, headline, summary, links)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProfileCreateResponse: Created profile with id, userId, full_name, headline, created_at

    Raises:
        HTTPException: If validation fails, user not found, or profile already exists
    """
    try:
        logger.info(
            f"Profile creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        service = ProfileServiceClass()
        profile = service.create_profile(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Profile creation endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "profileId": str(profile.id)},
        )

        return profile

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in profile creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in profile creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=ProfileGetResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProfileGetResponse: User profile data with all details

    Raises:
        HTTPException: If user not found or profile doesn't exist
    """
    try:
        logger.info(
            f"Profile retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        service = ProfileServiceClass()
        profile = service.get_profile(db=db, userId=str(current_user.id))

        logger.info(
            f"Profile retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "profileId": str(profile.id)},
        )

        return profile

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in profile retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in profile retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current authenticated user profile.

    Args:
        data: Profile update request data (optional fields: full_name, headline, summary, links)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProfileUpdateResponse: Updated profile data

    Raises:
        HTTPException: If validation fails, user not found, or profile doesn't exist
    """
    try:
        logger.info(
            f"Profile update request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        service = ProfileServiceClass()
        profile = service.update_profile(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Profile update endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "profileId": str(profile.id)},
        )

        return profile

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in profile update: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in profile update endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/",
    response_model=ProfileDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def delete_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete current authenticated user profile.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProfileDeleteResponse: Deletion confirmation with profile details

    Raises:
        HTTPException: If user not found or profile doesn't exist
    """
    try:
        logger.info(
            f"Profile deletion request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        service = ProfileServiceClass()
        response = service.delete_profile(db=db, userId=str(current_user.id))

        logger.info(
            f"Profile deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "profileId": str(response.id)},
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in profile deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in profile deletion endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
