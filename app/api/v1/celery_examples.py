"""
Example API routes showing how to use Celery tasks
Add these to your existing router.py as examples
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.helpers.celery_helpers import TaskHelper, QuickTasks
from app.core.logger import logger

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


# ==================== Request/Response Models ====================
class ResumeGenerationRequest(BaseModel):
    """Request to generate resume"""

    user_data: dict
    job_description: str
    template: str = "default"


class PDFGenerationRequest(BaseModel):
    """Request to generate PDF"""

    user_id: str
    content_data: dict
    template: str = "default"


class TaskStatusResponse(BaseModel):
    """Response with task status"""

    task_id: str
    status: str
    data: dict = None


# ==================== Resume Generation Routes ====================


@router.post("/generate-resume")
async def generate_resume(request: ResumeGenerationRequest):
    """
    Generate resume using AI in background

    Example response:
    {
        "task_id": "abc123xyz",
        "status": "submitted",
        "message": "Resume generation started. Check status with this task_id"
    }
    """
    try:
        task_id = QuickTasks.generate_resume(request.user_data, request.job_description)

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Resume generation started",
            "check_status_url": f"/api/v1/tasks/status/{task_id}",
        }
    except Exception as e:
        logger.error(f"Failed to submit resume generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-resume-pdf")
async def generate_resume_pdf(request: PDFGenerationRequest):
    """
    Generate resume PDF in background

    Example response:
    {
        "task_id": "xyz789abc",
        "status": "submitted",
        "message": "PDF generation started"
    }
    """
    try:
        task_id = QuickTasks.generate_resume_pdf(
            request.user_id, request.content_data, request.template
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "PDF generation started",
            "check_status_url": f"/api/v1/tasks/status/{task_id}",
        }
    except Exception as e:
        logger.error(f"Failed to submit PDF generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Cover Letter Routes ====================


@router.post("/generate-cover-letter")
async def generate_cover_letter(request: ResumeGenerationRequest):
    """
    Generate cover letter using AI in background
    """
    try:
        task_id = QuickTasks.generate_cover_letter(
            request.user_data, request.job_description
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Cover letter generation started",
            "check_status_url": f"/api/v1/tasks/status/{task_id}",
        }
    except Exception as e:
        logger.error(f"Failed to submit cover letter generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-cover-letter-pdf")
async def generate_cover_letter_pdf(request: PDFGenerationRequest):
    """
    Generate cover letter PDF in background
    """
    try:
        task_id = QuickTasks.generate_cover_letter_pdf(
            request.user_id, request.content_data, request.template
        )

        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Cover letter PDF generation started",
            "check_status_url": f"/api/v1/tasks/status/{task_id}",
        }
    except Exception as e:
        logger.error(f"Failed to submit cover letter PDF generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Task Status Routes ====================


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a task

    Example response:
    {
        "task_id": "abc123xyz",
        "status": "SUCCESS",
        "result": {...generated content...}
    }

    Possible statuses:
    - PENDING: Task is waiting
    - PROGRESS: Task is running
    - SUCCESS: Task completed
    - FAILURE: Task failed
    - RETRY: Task is being retried
    """
    try:
        status = TaskHelper.get_task_status(task_id)
        return {"task_id": task_id, **status}
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running task

    Example response:
    {
        "task_id": "abc123xyz",
        "cancelled": true
    }
    """
    try:
        success = TaskHelper.revoke_task(task_id)
        return {"task_id": task_id, "cancelled": success}
    except Exception as e:
        logger.error(f"Failed to cancel task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
