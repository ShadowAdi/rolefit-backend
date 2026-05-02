"""
Tasks Package
Import all tasks here so Celery can discover them
"""

from .ai_tasks import (
    generate_resume_with_ai,
    generate_cover_letter_with_ai,
    parse_job_description,
    cleanup_old_tasks,
)

from .pdf_tasks import (
    generate_resume_pdf,
    generate_cover_letter_pdf,
    generate_resume_and_cover_letter,
)

__all__ = [
    "generate_resume_with_ai",
    "generate_cover_letter_with_ai",
    "parse_job_description",
    "cleanup_old_tasks",
    "generate_resume_pdf",
    "generate_cover_letter_pdf",
    "generate_resume_and_cover_letter",
]
