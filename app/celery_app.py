"""
Celery App Configuration
Simple explanation: This is where we set up our background task worker
"""

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "rolefit",
    broker=REDIS_URL,  # Where tasks are stored (Redis)
    backend=REDIS_URL,  # Where results are stored (Redis)
)

# Configure Celery
celery_app.conf.update(
    # How long to wait for task result
    result_expires=3600,  # 1 hour
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # This makes tasks more reliable
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry failed tasks
    task_autoretry_for={"exc": Exception, "max_retries": 3, "countdown": 5},
)

# Optional: Schedule periodic tasks (like background jobs)
celery_app.conf.beat_schedule = {
    # Example: Clean up old cache entries every hour
    "cleanup-old-tasks": {
        "task": "app.tasks.ai_tasks.cleanup_old_tasks",
        "schedule": crontab(minute=0),  # Every hour
    },
}
