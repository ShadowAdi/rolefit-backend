from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Experience import ExperienceCreateRequest, ExperienceUpdateRequest
from app.response.experience_responses import (
    ExperienceCreateResponse,
    ExperienceGetResponse,
    ExperienceUpdateResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .experience_service import ExperienceServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Experience"])

ExperienceService = ExperienceServiceClass()


@router.post(
    "/",
    response_model=ExperienceCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    data: ExperienceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new experience for the authenticated user.

    Args:
        data: Experience creation request data (company_name, role, description, techStack, employment_type, location_type, location_details, start_month, start_year, end_month, end_year)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ExperienceCreateResponse: Created experience with id, company_name, role, profileId, created_at

    Raises:
        HTTPException: If validation fails, user/profile not found, or database error
    """
    try:
        logger.info(
            f"Experience creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        experience = ExperienceService.create_experience(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Experience creation endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "experienceId": str(experience.id)},
        )

        return experience

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in experience creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in experience creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[ExperienceGetResponse],
    status_code=status.HTTP_200_OK,
)
async def list_experiences(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all experiences for the authenticated user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[ExperienceGetResponse]: List of user's experiences

    Raises:
        HTTPException: If user/profile not found
    """
    try:
        logger.info(
            f"Experience list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        experiences = ExperienceService.list_experiences(
            db=db, userId=str(current_user.id)
        )

        logger.info(
            f"Experience list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "experienceCount": len(experiences)},
        )

        return experiences

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in experience list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in experience list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{experienceId}",
    response_model=ExperienceGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_experience(
    experienceId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific experience for the authenticated user.

    Args:
        experienceId: Experience ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ExperienceGetResponse: Experience details with all information

    Raises:
        HTTPException: If user/profile/experience not found
    """
    try:
        logger.info(
            f"Experience retrieval request received for user: {current_user.id}, experience: {experienceId}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )

        experience = ExperienceService.get_experience(
            db=db, userId=str(current_user.id), experienceId=experienceId
        )

        logger.info(
            f"Experience retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "experienceId": str(experience.id)},
        )

        return experience

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in experience retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in experience retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "experienceId": experienceId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{experienceId}",
    response_model=ExperienceUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_experience(
    experienceId: str,
    data: ExperienceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing experience for the authenticated user.

    Args:
        experienceId: Experience ID to update
        data: Experience update request data (optional fields: company_name, role, description, techStack, employment_type, location_type, location_details, start_month, start_year, end_month, end_year)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ExperienceUpdateResponse: Updated experience data

    Raises:
        HTTPException: If validation fails, experience not found, or database error
    """
    try:
        logger.info(
            f"Experience update request received for user: {current_user.id}, experience: {experienceId}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )

        experience = ExperienceService.update_experience(
            db=db, payload=data, userId=str(current_user.id), experienceId=experienceId
        )

        logger.info(
            f"Experience update endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "experienceId": str(experience.id)},
        )

        return experience

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in experience update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in experience update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "experienceId": experienceId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{experienceId}",
    status_code=status.HTTP_200_OK,
)
async def delete_experience(
    experienceId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an experience for the authenticated user.

    Args:
        experienceId: Experience ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, id, company, and role

    Raises:
        HTTPException: If experience not found
    """
    try:
        logger.info(
            f"Experience deletion request received for user: {current_user.id}, experience: {experienceId}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )

        response = ExperienceService.delete_experience(
            db=db, userId=str(current_user.id), experienceId=experienceId
        )

        logger.info(
            f"Experience deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in experience deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "experienceId": experienceId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in experience deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "experienceId": experienceId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
