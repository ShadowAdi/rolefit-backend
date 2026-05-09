from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Academic import AcademicCreateRequest, AcademicUpdateRequest
from app.response.academic_responses import (
    AcademicCreateResponse,
    AcademicGetResponse,
    AcademicUpdateResponse,
)
from app.response.base import APIResponse
from sqlalchemy.orm import Session
from app.db.db import get_db
from .academics_service import AcademicServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Academics"])

AcademicService = AcademicServiceClass()


@router.post(
    "/",
    response_model=AcademicCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_academic(
    data: AcademicCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new academic record for the authenticated user.

    Args:
        data: Academic creation request data (degree_name, college_name, description, links, start_month, start_year, end_month, end_year)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AcademicCreateResponse: Created academic record with id, degree_name, college_name, profileId, created_at

    Raises:
        HTTPException: If validation fails, user/profile not found, or database error
    """
    try:
        logger.info(
            f"Academic creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        academic = await AcademicService.create_academic(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Academic creation endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "academicId": str(academic.id)},
        )

        return APIResponse(
            status_code=201,
            success=True,
            message="Academic Created Successfully",
            data=academic,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in academic creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in academic creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[AcademicGetResponse],
    status_code=status.HTTP_200_OK,
)
async def list_academics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all academic records for the authenticated user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[AcademicGetResponse]: List of user's academic records

    Raises:
        HTTPException: If user/profile not found
    """
    try:
        logger.info(
            f"Academic list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        academics = await AcademicService.list_academics(
            db=db, userId=str(current_user.id)
        )

        logger.info(
            f"Academic list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "academicCount": len(academics)},
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Academic Fetched Successfully",
            data=academics,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in academic list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in academic list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{academicId}",
    response_model=AcademicGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_academic(
    academicId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific academic record for the authenticated user.

    Args:
        academicId: Academic record ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AcademicGetResponse: Academic record details with all information

    Raises:
        HTTPException: If user/profile/academic record not found
    """
    try:
        logger.info(
            f"Academic retrieval request received for user: {current_user.id}, academic: {academicId}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )

        academic = await AcademicService.get_academic(
            db=db, userId=str(current_user.id), academicId=academicId
        )

        logger.info(
            f"Academic retrieval endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "academicId": str(academic.id)},
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Academic Fetched Successfully",
            data=academic,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in academic retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in academic retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "academicId": academicId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{academicId}",
    response_model=AcademicUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_academic(
    academicId: str,
    data: AcademicUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing academic record for the authenticated user.

    Args:
        academicId: Academic record ID to update
        data: Academic update request data (optional fields: degree_name, college_name, description, links, start_month, start_year, end_month, end_year)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        AcademicUpdateResponse: Updated academic record data

    Raises:
        HTTPException: If validation fails, academic record not found, or database error
    """
    try:
        logger.info(
            f"Academic update request received for user: {current_user.id}, academic: {academicId}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )

        academic = await AcademicService.update_academic(
            db=db, payload=data, userId=str(current_user.id), academicId=academicId
        )

        logger.info(
            f"Academic update endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "academicId": str(academic.id)},
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Academic Updated Successfully",
            data=academic,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in academic update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in academic update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "academicId": academicId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{academicId}",
    status_code=status.HTTP_200_OK,
)
async def delete_academic(
    academicId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an academic record for the authenticated user.

    Args:
        academicId: Academic record ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, id, degree, and college

    Raises:
        HTTPException: If academic record not found
    """
    try:
        logger.info(
            f"Academic deletion request received for user: {current_user.id}, academic: {academicId}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )

        response = await AcademicService.delete_academic(
            db=db, userId=str(current_user.id), academicId=academicId
        )

        logger.info(
            f"Academic deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )

        return APIResponse(
            status_code=200,
            success=response.get("success"),
            message=response.get("message"),
            data={
                "deletedAcademicId": response.get("deletedAcademicId"),
                "degree": response.get("degree"),
                "college": response.get("college"),
            },
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in academic deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "academicId": academicId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in academic deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "academicId": academicId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
