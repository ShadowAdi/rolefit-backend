from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from app.dependency.dependencies import get_db, get_current_user
from app.api.v1.content.content_service import ContentServiceClass
from app.core.logger import logger
from app.models.GeneratedDocument import GeneratedDocumentEnumType
from app.schema.GeneratedDocument import (
    GeneratedDocumentApiResponse,
    GenerateContentApiResponse,
    GeneratedDocumentListApiResponse,
    DeleteDocumentApiResponse,
    DocumentStatusApiResponse,
)
from typing import Optional

router = APIRouter(prefix="", tags=["Content"])

content_service = ContentServiceClass()


@router.post(
    "/cover-letter/{jobId}",
    status_code=status.HTTP_201_CREATED,
    response_model=GenerateContentApiResponse,
)
async def generate_cover_letter_content(
    jobId: str,
    user_specifications: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    provider: Optional[str] = None,
):
    user_id = current_user.id
    logger.info(f"Creating cover letter content for user: {user_id}")
    try:
        result = await content_service.generate_cover_letter_content(
            userId=str(user_id),
            jobId=jobId,
            user_specifications=user_specifications,
            db=db,
            provider=provider,
        )
        return GenerateContentApiResponse(
            success=True,
            status_code=201,
            message="Cover letter generation queued. Poll /status/{doc_id} for updates.",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/item/{contentId}",
    status_code=status.HTTP_200_OK,
    response_model=GeneratedDocumentApiResponse,
)
async def get_content(
    contentId: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    try:
        result = content_service.get_content(
            userId=str(user_id), contentId=contentId, db=db
        )
        return GeneratedDocumentApiResponse(
            success=True,
            status_code=200,
            message="Content retrieved successfully",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error fetching content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/item/{contentId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteDocumentApiResponse,
)
async def delete_content(
    contentId: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    try:
        result = content_service.delete_content(
            userId=str(user_id), contentId=contentId, db=db
        )
        return DeleteDocumentApiResponse(
            success=True,
            status_code=200,
            message="Content deleted successfully",
            data={
                "id": str(result.id),
                "success": result.success,
                "message": result.message,
            },
        )
    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/status", response_model=DocumentStatusApiResponse)
async def get_document_status(
    doc_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Poll after POST /generate.
    When status == "completed" → call /preview or /download.
    When status == "failed"    → show error, offer retry.
    """
    user_id = current_user.id
    try:
        result = content_service.get_document_status(
            doc_id=doc_id, userId=str(user_id), db=db
        )
        return DocumentStatusApiResponse(
            success=True,
            status_code=200,
            message="Document status retrieved",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error fetching document status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{jobId}",
    status_code=status.HTTP_201_CREATED,
    response_model=GenerateContentApiResponse,
)
async def generate_resume_content(
    jobId: str,
    user_specifications: str = Query(None),
    provider: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if provider:
        valid_providers = ["groq", "openai", "anthropic", "google"]
        if provider.lower() not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
            )
    user_id = current_user.id
    logger.info(f"Creating resume content for user: {user_id}")
    try:
        result = await content_service.generate_resume_content(
            userId=str(user_id),
            jobId=jobId,
            user_specifications=user_specifications,
            db=db,
            provider=provider,
        )
        return GenerateContentApiResponse(
            success=True,
            status_code=201,
            message="Resume generation queued. Poll /status/{doc_id} for updates.",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=GeneratedDocumentListApiResponse,
)
async def get_all_user_contents(
    content_type: GeneratedDocumentEnumType = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all generated content for the current user across all JDs"""
    user_id = current_user.id
    try:
        result = content_service.get_all_user_contents(
            userId=str(user_id), content_type=content_type, db=db
        )
        return GeneratedDocumentListApiResponse(
            success=True,
            status_code=200,
            message="All contents retrieved successfully",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error fetching all contents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{jobId}",
    status_code=status.HTTP_200_OK,
    response_model=GeneratedDocumentListApiResponse,
)
async def get_all_contents(
    jobId: str,
    content_type: GeneratedDocumentEnumType = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    try:
        result = content_service.get_all_contents(
            userId=str(user_id), jobId=jobId, content_type=content_type, db=db
        )
        return GeneratedDocumentListApiResponse(
            success=True,
            status_code=200,
            message="Contents retrieved successfully",
            data=result,
        )
    except Exception as e:
        logger.error(f"Error fetching contents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
