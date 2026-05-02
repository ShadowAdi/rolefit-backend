"""
AI Tasks Module
Handles all AI API calls as background tasks
"""

from celery import shared_task
from app.core.logger import logger
from app.helpers.resume_prompt import get_resume_prompt
from app.helpers.cover_letter_prompt import get_cover_letter_prompt
from app.utils.call_groq import call_groq_api
from app.utils.call_sarvam import call_sarvam_api
import json


@shared_task(bind=True, name="app.tasks.ai_tasks.generate_resume_with_ai")
def generate_resume_with_ai(self, user_data: dict, jd_content: str):
    """
    Background task to generate resume using AI

    Args:
        user_data: User profile and experience data
        jd_content: Job description content

    Returns:
        Generated resume content
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting resume generation")

        # Build prompt
        prompt = get_resume_prompt(user_data, jd_content)

        # Call AI API (Groq or Sarvam)
        ai_response = call_groq_api(prompt)

        logger.info(f"[Task {self.request.id}] Resume generation completed")
        return {"status": "success", "data": ai_response, "task_id": self.request.id}
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Resume generation failed: {str(e)}")
        return {"status": "error", "error": str(e), "task_id": self.request.id}


@shared_task(bind=True, name="app.tasks.ai_tasks.generate_cover_letter_with_ai")
def generate_cover_letter_with_ai(self, user_data: dict, jd_content: str):
    """
    Background task to generate cover letter using AI

    Args:
        user_data: User profile data
        jd_content: Job description content

    Returns:
        Generated cover letter content
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting cover letter generation")

        # Build prompt
        prompt = get_cover_letter_prompt(user_data, jd_content)

        # Call AI API
        ai_response = call_groq_api(prompt)

        logger.info(f"[Task {self.request.id}] Cover letter generation completed")
        return {"status": "success", "data": ai_response, "task_id": self.request.id}
    except Exception as e:
        logger.error(
            f"[Task {self.request.id}] Cover letter generation failed: {str(e)}"
        )
        return {"status": "error", "error": str(e), "task_id": self.request.id}


@shared_task(bind=True, name="app.tasks.ai_tasks.parse_job_description")
def parse_job_description(self, jd_content: str):
    """
    Background task to parse job description using AI

    Args:
        jd_content: Raw job description text

    Returns:
        Parsed job description
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting JD parsing")

        prompt = f"""Parse this job description and extract: 
        1. Key responsibilities
        2. Required skills
        3. Required experience
        4. Tools/Technologies
        
        Job Description:
        {jd_content}
        
        Return as JSON"""

        ai_response = call_groq_api(prompt)

        logger.info(f"[Task {self.request.id}] JD parsing completed")
        return {"status": "success", "data": ai_response, "task_id": self.request.id}
    except Exception as e:
        logger.error(f"[Task {self.request.id}] JD parsing failed: {str(e)}")
        return {"status": "error", "error": str(e), "task_id": self.request.id}


@shared_task(bind=True, name="app.tasks.ai_tasks.cleanup_old_tasks")
def cleanup_old_tasks(self):
    """
    Cleanup task - runs periodically to clean up old cached tasks
    """
    try:
        logger.info("Running cleanup task")
        # You can add cleanup logic here
        return {"status": "success", "message": "Cleanup completed"}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return {"status": "error", "error": str(e)}
