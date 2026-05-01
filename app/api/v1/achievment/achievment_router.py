from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Achievement import AchievementCreateRequest, AchievementUpdateRequest
from app.response.achievement_responses import (
    AchievementCreateResponse,
    AchievementGetResponse,
    AchievementUpdateResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .achievment_service import AchievementServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Achievements"])

AchievementService = AchievementServiceClass()


@router.post(
    "/",
    response_model=AchievementCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_achievement(
    data: AchievementCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new achievement record for the authenticated user.

    Args:
        data: Achievement creation request data (title, achievement_type, description, location, start_month, start_year, end_month, end_year, links)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AchievementCreateResponse: Created achievement record with id, title, achievement_type, profileId, created_at

    Raises:
        HTTPException: If validation fails, user/profile not found, or database error
    """
    try:
        logger.info(
            f"Achievement creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        achievement = await AchievementService.create_achievement(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Achievement creation endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "achievementId": str(achievement.id),
            },
        )

        return achievement

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in achievement creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[AchievementGetResponse],
    status_code=status.HTTP_200_OK,
)
async def list_achievements(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all achievement records for the authenticated user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[AchievementGetResponse]: List of user's achievement records

    Raises:
        HTTPException: If user/profile not found
    """
    try:
        logger.info(
            f"Achievement list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        achievements = await AchievementService.list_achievements(
            db=db, userId=str(current_user.id)
        )

        logger.info(
            f"Achievement list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "achievementCount": len(achievements),
            },
        )

        return achievements

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in achievement list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{achievementId}",
    response_model=AchievementGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_achievement(
    achievementId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific achievement record for the authenticated user.

    Args:
        achievementId: Achievement record ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AchievementGetResponse: Achievement record details with all information

    Raises:
        HTTPException: If user/profile/achievement record not found
    """
    try:
        logger.info(
            f"Achievement retrieval request received for user: {current_user.id}, achievement: {achievementId}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )

        achievement = await AchievementService.get_achievement(
            db=db, userId=str(current_user.id), achievementId=achievementId
        )

        logger.info(
            f"Achievement retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "achievementId": str(achievement.id),
            },
        )

        return achievement

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in achievement retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "achievementId": achievementId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{achievementId}",
    response_model=AchievementUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_achievement(
    achievementId: str,
    data: AchievementUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing achievement record for the authenticated user.

    Args:
        achievementId: Achievement record ID to update
        data: Achievement update request data (optional fields: title, achievement_type, description, location, start_month, start_year, end_month, end_year, links)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AchievementUpdateResponse: Updated achievement record data

    Raises:
        HTTPException: If validation fails, achievement record not found, or database error
    """
    try:
        logger.info(
            f"Achievement update request received for user: {current_user.id}, achievement: {achievementId}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )

        achievement = await AchievementService.update_achievement(
            db=db,
            payload=data,
            userId=str(current_user.id),
            achievementId=achievementId,
        )

        logger.info(
            f"Achievement update endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "achievementId": str(achievement.id),
            },
        )

        return achievement

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in achievement update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "achievementId": achievementId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{achievementId}",
    status_code=status.HTTP_200_OK,
)
async def delete_achievement(
    achievementId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an achievement record for the authenticated user.

    Args:
        achievementId: Achievement record ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, id, title, and type

    Raises:
        HTTPException: If achievement record not found
    """
    try:
        logger.info(
            f"Achievement deletion request received for user: {current_user.id}, achievement: {achievementId}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )

        response = await AchievementService.delete_achievement(
            db=db, userId=str(current_user.id), achievementId=achievementId
        )

        logger.info(
            f"Achievement deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in achievement deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "achievementId": achievementId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "achievementId": achievementId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
