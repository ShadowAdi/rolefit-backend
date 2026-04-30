from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Skill import (
    SkillCreateRequest,
    SkillUpdateRequest,
    AddSkillToUserRequest,
)
from app.response.skill_responses import (
    SkillCreateResponse,
    SkillGetResponse,
    SkillListResponse,
    SkillUpdateResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .skill_service import SkillServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Skills"])

SkillService = SkillServiceClass()


@router.post(
    "/",
    response_model=SkillCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    data: SkillCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new skill in the system for the authenticated user.

    Args:
        data: Skill creation request data (name)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        SkillCreateResponse: Created skill with id, name, created_by, created_at

    Raises:
        HTTPException: If validation fails, user not found, skill already exists, or database error
    """
    try:
        logger.info(
            f"Skill creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        skill = SkillService.create_skill(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Skill creation endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillId": str(skill.id),
            },
        )

        return skill

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in skill creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in skill creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[SkillListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_skills(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all available skills in the system or user's skills.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[SkillListResponse]: List of all available skills

    Raises:
        HTTPException: If database error occurs
    """
    try:
        logger.info(
            f"Skill list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        skills = SkillService.list_skills(db=db)

        logger.info(
            f"Skill list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillCount": len(skills),
            },
        )

        return skills

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in skill list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in skill list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{skillId}",
    response_model=SkillGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_skill(
    skillId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific skill by ID.

    Args:
        skillId: Skill ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        SkillGetResponse: Skill details with all information

    Raises:
        HTTPException: If skill not found or database error
    """
    try:
        logger.info(
            f"Skill retrieval request received for user: {current_user.id}, skill: {skillId}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        skill = SkillService.get_skill(db=db, skillId=skillId)

        logger.info(
            f"Skill retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillId": str(skill.id),
            },
        )

        return skill

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in skill retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in skill retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "skillId": skillId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{skillId}",
    response_model=SkillUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_skill(
    skillId: str,
    data: SkillUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing skill for the authenticated user (only creator can update).

    Args:
        skillId: Skill ID to update
        data: Skill update request data (name)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        SkillUpdateResponse: Updated skill data

    Raises:
        HTTPException: If validation fails, skill not found, not authorized, or database error
    """
    try:
        logger.info(
            f"Skill update request received for user: {current_user.id}, skill: {skillId}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        skill = SkillService.update_skill(
            db=db,
            skillId=skillId,
            payload=data,
            userId=str(current_user.id),
        )

        logger.info(
            f"Skill update endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillId": str(skill.id),
            },
        )

        return skill

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in skill update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in skill update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "skillId": skillId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{skillId}",
    status_code=status.HTTP_200_OK,
)
async def delete_skill(
    skillId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a skill (only creator can delete).

    Args:
        skillId: Skill ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, skillId, and skillName

    Raises:
        HTTPException: If skill not found, not authorized, or database error
    """
    try:
        logger.info(
            f"Skill deletion request received for user: {current_user.id}, skill: {skillId}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        response = SkillService.delete_skill(
            db=db, skillId=skillId, userId=str(current_user.id)
        )

        logger.info(
            f"Skill deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in skill deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in skill deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "skillId": skillId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post(
    "/user/add",
    status_code=status.HTTP_200_OK,
)
async def add_skill_to_user(
    data: AddSkillToUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a skill to user's profile.

    Handles two scenarios in one API call:
    1. User selects existing skill: Send skillId -> add directly
    2. User types new skill name: Send skillName -> create if doesn't exist, then add

    Args:
        data: AddSkillToUserRequest with either skillId or skillName
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Success message with skillId, skillName, and skillCreated flag

    Raises:
        HTTPException: If validation fails, user not found, or database error
    """
    try:
        logger.info(
            f"Add skill to user request received for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillId": data.skillId,
                "skillName": data.skillName,
            },
        )

        response = SkillService.add_skill_to_user(
            db=db, userId=str(current_user.id), payload=data
        )

        logger.info(
            f"Add skill to user endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "skillId": response.get("skillId"),
            },
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in add skill to user: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in add skill to user endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/user/remove/{skillId}",
    status_code=status.HTTP_200_OK,
)
async def remove_skill_from_user(
    skillId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a skill from user's profile.

    Args:
        skillId: Skill ID to remove
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Success message with skillId

    Raises:
        HTTPException: If user doesn't have skill or database error
    """
    try:
        logger.info(
            f"Remove skill from user request received for user: {current_user.id}, skill: {skillId}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        response = SkillService.remove_skill_from_user(
            db=db, userId=str(current_user.id), skillId=skillId
        )

        logger.info(
            f"Remove skill from user endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )

        return response

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in remove skill from user: {http_exc.detail}",
            extra={"userId": str(current_user.id), "skillId": skillId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in remove skill from user endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "skillId": skillId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
