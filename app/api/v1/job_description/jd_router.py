from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from app.dependency.dependencies import get_db, get_current_user
from app.schema.JobDescription import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
)
from app.api.v1.job_description.jd_service import JobDescriptionClass
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Job Descriptions"])

jd_service = JobDescriptionClass()


@router.post(
    "/",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Creating job description for user: {user_id}")
    return jd_service.create_jd(db, user_id, payload)


@router.get(
    "/{jd_id}",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_job_description(
    jd_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Retrieving job description {jd_id} for user: {user_id}")
    return jd_service.get_jd(db, jd_id, user_id)


@router.get(
    "/",
    response_model=List[JobDescriptionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_job_descriptions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Retrieving all job descriptions for user: {user_id}")
    return jd_service.get_all_jds(db, user_id)


@router.patch(
    "/{jd_id}",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_job_description(
    jd_id: str,
    payload: JobDescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Updating job description {jd_id} for user: {user_id}")
    return jd_service.update_jd(db, jd_id, user_id, payload)


@router.post(
    "/generate",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_job_description(
    payload: str = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Generating job description from raw JD for user: {user_id}")
    return jd_service.generate_jd(db, user_id, payload)


@router.delete(
    "/{jd_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job_description(
    jd_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id") or current_user.get("id")
    logger.info(f"Deleting job description {jd_id} for user: {user_id}")
    return jd_service.delete_jd(db, jd_id, user_id)
