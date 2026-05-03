import os
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CELERY_URL = os.getenv("REDIS_CELERY_URL", "redis://localhost:6379/0")


celery_app = Celery(name="Rolefit_worker", broker=REDIS_CELERY_URL, backend=REDIS_URL)

# Register tasks from app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_autoretry_for={"exc": Exception, "max_retries": 3, "countdown": 5},
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "app.tasks.ai_tasks.cleanup_old_tasks",
        "schedule": crontab(minute=0),
    }
}
