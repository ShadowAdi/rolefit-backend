"""
PDF Generation Tasks
Handles all PDF generation as background tasks
"""

from celery import shared_task
from app.core.logger import logger
from app.helpers.build_pdf import build_pdf_resume
from app.helpers.build_pdf_bold import build_pdf_bold_resume
from app.helpers.build_pdf_minimalist import build_pdf_minimalist_resume
from app.helpers.build_pdf_sidebar import build_pdf_sidebar_resume
from app.helpers.buid_cover_letter_pdf import build_cover_letter_pdf
from app.helpers.build_cover_letter_bold import build_cover_letter_bold
from app.helpers.build_cover_letter_minimal import build_cover_letter_minimal
from app.db import redis_db
import os


@shared_task(bind=True, name="app.tasks.pdf_tasks.generate_resume_pdf")
def generate_resume_pdf(
    self, user_id: str, resume_data: dict, template: str = "default"
):
    """
    Background task to generate resume PDF

    Args:
        user_id: User ID
        resume_data: Resume content and styling data
        template: Template name (default, bold, minimalist, sidebar)

    Returns:
        Path to generated PDF file
    """
    try:
        logger.info(
            f"[Task {self.request.id}] Starting PDF generation for user {user_id}, template: {template}"
        )

        # Choose template builder
        if template == "bold":
            pdf_path = build_pdf_bold_resume(user_id, resume_data)
        elif template == "minimalist":
            pdf_path = build_pdf_minimalist_resume(user_id, resume_data)
        elif template == "sidebar":
            pdf_path = build_pdf_sidebar_resume(user_id, resume_data)
        else:
            pdf_path = build_pdf_resume(user_id, resume_data)

        logger.info(
            f"[Task {self.request.id}] PDF generated successfully at {pdf_path}"
        )

        # Store the result in Redis (with task ID as key)
        # This way users can download it later
        await redis_db.redis_client.set(
            f"pdf_task_{self.request.id}", pdf_path, ex=86400  # Expire in 24 hours
        )

        return {"status": "success", "pdf_path": pdf_path, "task_id": self.request.id}
    except Exception as e:
        logger.error(f"[Task {self.request.id}] PDF generation failed: {str(e)}")
        return {"status": "error", "error": str(e), "task_id": self.request.id}


@shared_task(bind=True, name="app.tasks.pdf_tasks.generate_cover_letter_pdf")
def generate_cover_letter_pdf(
    self, user_id: str, cover_letter_data: dict, template: str = "default"
):
    """
    Background task to generate cover letter PDF

    Args:
        user_id: User ID
        cover_letter_data: Cover letter content and styling data
        template: Template name (default, bold, minimal)

    Returns:
        Path to generated PDF file
    """
    try:
        logger.info(
            f"[Task {self.request.id}] Starting cover letter PDF generation for user {user_id}, template: {template}"
        )

        # Choose template builder
        if template == "bold":
            pdf_path = build_cover_letter_bold(user_id, cover_letter_data)
        elif template == "minimal":
            pdf_path = build_cover_letter_minimal(user_id, cover_letter_data)
        else:
            pdf_path = build_cover_letter_pdf(user_id, cover_letter_data)

        logger.info(
            f"[Task {self.request.id}] Cover letter PDF generated successfully at {pdf_path}"
        )

        # Store in Redis for later retrieval
        await redis_db.redis_client.set(
            f"cover_letter_pdf_task_{self.request.id}",
            pdf_path,
            ex=86400,  # Expire in 24 hours
        )

        return {"status": "success", "pdf_path": pdf_path, "task_id": self.request.id}
    except Exception as e:
        logger.error(
            f"[Task {self.request.id}] Cover letter PDF generation failed: {str(e)}"
        )
        return {"status": "error", "error": str(e), "task_id": self.request.id}


@shared_task(bind=True, name="app.tasks.pdf_tasks.generate_resume_and_cover_letter")
def generate_resume_and_cover_letter(
    self,
    user_id: str,
    resume_data: dict,
    cover_letter_data: dict,
    resume_template: str = "default",
    cover_letter_template: str = "default",
):
    """
    Background task to generate both resume and cover letter PDFs
    Great for bulk operations!

    Args:
        user_id: User ID
        resume_data: Resume content
        cover_letter_data: Cover letter content
        resume_template: Resume template name
        cover_letter_template: Cover letter template name

    Returns:
        Paths to both generated PDFs
    """
    try:
        logger.info(
            f"[Task {self.request.id}] Starting dual document generation for user {user_id}"
        )

        # Generate resume
        if resume_template == "bold":
            resume_pdf = build_pdf_bold_resume(user_id, resume_data)
        elif resume_template == "minimalist":
            resume_pdf = build_pdf_minimalist_resume(user_id, resume_data)
        elif resume_template == "sidebar":
            resume_pdf = build_pdf_sidebar_resume(user_id, resume_data)
        else:
            resume_pdf = build_pdf_resume(user_id, resume_data)

        # Generate cover letter
        if cover_letter_template == "bold":
            cover_letter_pdf = build_cover_letter_bold(user_id, cover_letter_data)
        elif cover_letter_template == "minimal":
            cover_letter_pdf = build_cover_letter_minimal(user_id, cover_letter_data)
        else:
            cover_letter_pdf = build_cover_letter_pdf(user_id, cover_letter_data)

        logger.info(f"[Task {self.request.id}] Dual document generation completed")

        return {
            "status": "success",
            "resume_pdf": resume_pdf,
            "cover_letter_pdf": cover_letter_pdf,
            "task_id": self.request.id,
        }
    except Exception as e:
        logger.error(
            f"[Task {self.request.id}] Dual document generation failed: {str(e)}"
        )
        return {"status": "error", "error": str(e), "task_id": self.request.id}
