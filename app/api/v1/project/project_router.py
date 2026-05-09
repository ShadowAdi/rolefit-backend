from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from app.response.project_responses import (
    ProjectCreateResponse,
    ProjectGetResponse,
    ProjectUpdateResponse,
    ProjectListResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .project_service import ProjectService
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from app.response.base import APIResponse
from typing import List

router = APIRouter(prefix="", tags=["Project"])


@router.post(
    "/",
    response_model=ProjectCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new project for the authenticated user.

    Args:
        data: Project creation request data (title, description, techStack, links, startDate, endDate)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProjectCreateResponse: Created project with id, title, profileId, created_at

    Raises:
        HTTPException: If validation fails, user/profile not found, or title duplicate
    """
    try:
        logger.info(
            f"Project creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        project = ProjectService.create_project(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Project creation endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "projectId": str(project.id)},
        )

        return APIResponse(
            status_code=201,
            message="Project Created Successfully",
            success=True,
            data=project,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in project creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in project creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[ProjectListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_projects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all projects for the authenticated user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[ProjectListResponse]: List of user's projects

    Raises:
        HTTPException: If user/profile not found
    """
    try:
        logger.info(
            f"Project list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        projects = ProjectService.list_projects(db=db, userId=str(current_user.id))

        logger.info(
            f"Project list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "projectCount": len(projects)},
        )

        return APIResponse(
            status_code=200,
            message="Project Fetched Successfully",
            success=True,
            data=projects,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in project list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in project list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{projectId}",
    response_model=ProjectGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    projectId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific project for the authenticated user.

    Args:
        projectId: Project ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProjectGetResponse: Project details with all information

    Raises:
        HTTPException: If user/profile/project not found
    """
    try:
        logger.info(
            f"Project retrieval request received for user: {current_user.id}, project: {projectId}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )

        project = ProjectService.get_project(
            db=db, userId=str(current_user.id), projectId=projectId
        )

        logger.info(
            f"Project retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "projectId": str(project.id)},
        )

        return APIResponse(
            status_code=200,
            message="Project Fetched Successfully",
            success=True,
            data=project,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in project retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in project retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "projectId": projectId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{projectId}",
    response_model=ProjectUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    projectId: str,
    data: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing project for the authenticated user.

    Args:
        projectId: Project ID to update
        data: Project update request data (optional fields: title, description, techStack, links, startDate, endDate)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ProjectUpdateResponse: Updated project data

    Raises:
        HTTPException: If validation fails, project not found, or title duplicate
    """
    try:
        logger.info(
            f"Project update request received for user: {current_user.id}, project: {projectId}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )

        project = ProjectService.update_project(
            db=db, payload=data, userId=str(current_user.id), projectId=projectId
        )

        logger.info(
            f"Project update endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "projectId": str(project.id)},
        )

        return APIResponse(
            status_code=200,
            message="Project Updated Successfully",
            success=True,
            data=project,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in project update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in project update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "projectId": projectId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{projectId}",
    status_code=status.HTTP_200_OK,
)
async def delete_project(
    projectId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a project for the authenticated user.

    Args:
        projectId: Project ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, id, and title

    Raises:
        HTTPException: If project not found
    """
    try:
        logger.info(
            f"Project deletion request received for user: {current_user.id}, project: {projectId}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )

        response = ProjectService.delete_project(
            db=db, userId=str(current_user.id), projectId=projectId
        )

        logger.info(
            f"Project deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )

        return APIResponse(
            status_code=200,
            message="Project Deleted Successfully",
            success=True,
            data=response,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in project deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "projectId": projectId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in project deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "projectId": projectId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
