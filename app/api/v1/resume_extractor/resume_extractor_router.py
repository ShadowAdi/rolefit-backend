from fastapi import APIRouter, Depends, status, HTTPException
from .resume_extractor_service import ResumeExtractorServiceClass
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Resume Extractor"])

ResumeExtractorService = ResumeExtractorServiceClass()


@router.post(
    "/",
    response_model={
        "profile_id": str,
        "counts": {
            "experience": int,
            "academics": int,
            "achievements": int,
            "projects": int,
            "publications": int,
            "skills": int,
            "tools": int,
        },
    },
    status_code=status.HTTP_201_CREATED,
)
def resume_extractor(
    resume_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        resume_extractor = ResumeExtractorService.resumeextractor(
            db=db, resume_url=resume_url, userId=str(current_user.id)
        )

        return resume_extractor

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in resume extraction: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in resume extraction endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
