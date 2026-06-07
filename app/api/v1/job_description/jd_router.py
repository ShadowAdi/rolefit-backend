from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependency.dependencies import get_db, get_current_user
from app.schema.JobDescription import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
    JDInput,
)
from app.api.v1.job_description.jd_service import JobDescriptionClass
from app.core.logger import logger
from app.response.base import APIResponse
from typing import List
from app.models.User import User

router = APIRouter(prefix="", tags=["Job Descriptions"])

jd_service = JobDescriptionClass()


@router.post(
    "/",
    response_model=APIResponse[JobDescriptionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Creating job description for user: {str(user_id)}")
    jd = await jd_service.create_jd(db, str(user_id), payload)

    return APIResponse(
        status_code=201,
        message="Job description created successfully",
        success=True,
        data=jd,
    )


@router.post(
    "/generate",
    response_model=APIResponse[JobDescriptionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_job_description(
    body: JDInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Generating job description from raw JD for user: {current_user.id}")
    jd = await jd_service.generate_jd(db, str(user_id), body.payload, body.api_key_id)

    return APIResponse(
        status_code=201,
        message="Job description generated successfully",
        success=True,
        data=jd,
    )


@router.get(
    "/{jd_id}",
    response_model=APIResponse[JobDescriptionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_job_description(
    jd_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Retrieving job description {jd_id} for user: {user_id}")
    jd = await jd_service.get_jd(db, jd_id, str(user_id))

    return APIResponse(
        status_code=200,
        message="Job description retrieved successfully",
        success=True,
        data=jd,
    )


@router.get(
    "/",
    response_model=APIResponse[List[JobDescriptionResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_all_job_descriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Retrieving all job descriptions for user: {str(user_id)}")
    jds = await jd_service.get_all_jds(db, str(user_id))

    return APIResponse(
        status_code=200,
        message="Job descriptions retrieved successfully",
        success=True,
        data=jds,
    )


@router.patch(
    "/{jd_id}",
    response_model=APIResponse[JobDescriptionResponse],
    status_code=status.HTTP_200_OK,
)
async def update_job_description(
    jd_id: str,
    payload: JobDescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Updating job description {jd_id} for user: {str(user_id)}")
    jd = await jd_service.update_jd(db, jd_id, str(user_id), payload)

    return APIResponse(
        status_code=200,
        message="Job description updated successfully",
        success=True,
        data=jd,
    )


@router.get(
    "/test-ai",
    status_code=status.HTTP_200_OK,
)
async def test_jd(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id
    return await jd_service.test_jd(db, str(user_id))


@router.delete(
    "/{jd_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_job_description(
    jd_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(f"Deleting job description {jd_id} for user: {user_id}")
    await jd_service.delete_jd(db, jd_id, str(user_id))

    return APIResponse(
        status_code=200,
        message="Job description deleted successfully",
        success=True,
    )
