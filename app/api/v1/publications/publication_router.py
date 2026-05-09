from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Publication import (
    PublicationCreateRequest,
    PublicationUpdateRequest,
)
from app.response.publication_responses import (
    PublicationCreateResponse,
    PublicationGetResponse,
    PublicationUpdateResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .publication_service import PublicationServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List
from app.response.base import APIResponse

router = APIRouter(prefix="", tags=["Publications"])

PublicationService = PublicationServiceClass()


@router.post(
    "/",
    response_model=APIResponse[PublicationCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_publication(
    data: PublicationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new publication for the authenticated user.

    Args:
        data: Publication creation request data (title, publisher, publication_date, authors, description, url)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        PublicationCreateResponse: Created publication with id, title, publisher, profileId, created_at

    Raises:
        HTTPException: If validation fails, user/profile not found, or database error
    """
    try:
        logger.info(
            f"Publication creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        publication = await PublicationService.create_publication(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Publication creation endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "publicationId": str(publication.id),
            },
        )

        return APIResponse(
            status_code=201,
            message="Publication Created Successfully",
            success=True,
            data=publication,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in publication creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in publication creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=APIResponse[List[PublicationGetResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_publications(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all publications for the authenticated user.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[PublicationGetResponse]: List of user's publications

    Raises:
        HTTPException: If user/profile not found
    """
    try:
        logger.info(
            f"Publication list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        publications = await PublicationService.list_publications(
            db=db, userId=str(current_user.id)
        )

        logger.info(
            f"Publication list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "publicationCount": len(publications),
            },
        )

        return APIResponse(
            status_code=200,
            message="Publication Fetched Successfully",
            success=True,
            data=publications,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in publication list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in publication list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{publicationId}",
    response_model=APIResponse[PublicationGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_publication(
    publicationId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific publication for the authenticated user.

    Args:
        publicationId: Publication ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        PublicationGetResponse: Publication details with all information

    Raises:
        HTTPException: If user/profile/publication not found
    """
    try:
        logger.info(
            f"Publication retrieval request received for user: {current_user.id}, publication: {publicationId}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )

        publication = await PublicationService.get_publication(
            db=db, userId=str(current_user.id), publicationId=publicationId
        )

        logger.info(
            f"Publication retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "publicationId": str(publication.id),
            },
        )

        return APIResponse(
            status_code=200,
            message="Publication Fetched Successfully",
            success=True,
            data=publication,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in publication retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in publication retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "publicationId": publicationId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{publicationId}",
    response_model=APIResponse[PublicationUpdateResponse],
    status_code=status.HTTP_200_OK,
)
async def update_publication(
    publicationId: str,
    data: PublicationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing publication for the authenticated user.

    Args:
        publicationId: Publication ID to update
        data: Publication update request data (optional fields: title, publisher, publication_date, authors, description, url)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        PublicationUpdateResponse: Updated publication data

    Raises:
        HTTPException: If validation fails, publication not found, or database error
    """
    try:
        logger.info(
            f"Publication update request received for user: {current_user.id}, publication: {publicationId}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )

        publication = await PublicationService.update_publication(
            db=db,
            payload=data,
            userId=str(current_user.id),
            publicationId=publicationId,
        )

        logger.info(
            f"Publication update endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "publicationId": str(publication.id),
            },
        )

        return APIResponse(
            status_code=200,
            message="Publication Updated Successfully",
            success=True,
            data=publication,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in publication update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in publication update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "publicationId": publicationId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{publicationId}",
    status_code=status.HTTP_200_OK,
)
async def delete_publication(
    publicationId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a publication for the authenticated user.

    Args:
        publicationId: Publication ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, id, title, and publisher

    Raises:
        HTTPException: If publication not found
    """
    try:
        logger.info(
            f"Publication deletion request received for user: {current_user.id}, publication: {publicationId}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )

        response = await PublicationService.delete_publication(
            db=db, userId=str(current_user.id), publicationId=publicationId
        )

        logger.info(
            f"Publication deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )

        return APIResponse(
            status_code=200,
            message="Publication Deleted Successfully",
            success=True,
            data=response,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in publication deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "publicationId": publicationId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in publication deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "publicationId": publicationId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
