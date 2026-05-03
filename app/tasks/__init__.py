"""
Tasks Package
Import all tasks here so Celery can discover them
"""

from .ai_tasks import (
    generate_resume_task,
    generate_cover_letter_task,
    cleanup_old_tasks,
)

__all__ = [
    "generate_resume_task",
    "generate_cover_letter_task",
    "cleanup_old_tasks",
]
