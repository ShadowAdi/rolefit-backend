"""
Tasks Package
Import all tasks here so Celery can discover them
"""

from .ai_tasks import (
    generate_resume_task,
    generate_cover_letter_task,
    cleanup_old_tasks,
)

from .pdf_task import generate_resume_pdf
from .cover_letter_task import generate_cover_letter_pdf

__all__ = [
    "generate_resume_task",
    "generate_cover_letter_task",
    "cleanup_old_tasks",
    "generate_resume_pdf",
    "generate_cover_letter_pdf",
]
