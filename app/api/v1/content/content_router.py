from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependency.dependencies import get_db, get_current_user
from app.api.v1.content.content_service import ContentServiceClass
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Content"])

content_service = ContentServiceClass()


@router.post(
    "/{jobId}",
    status_code=status.HTTP_201_CREATED,
)
async def generate_content(
    jobId: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    logger.info(f"Creating job description for user: {user_id}")
    return content_service.generate_content(userId=str(user_id), jobId=jobId, db=db)
