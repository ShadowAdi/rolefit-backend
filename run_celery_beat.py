from app.core.celery_app import celery_app
from app.core.logger import logger

if __name__ == "__main__":
    logger.info("Starting Celery Beat Scheduler...")
    celery_app.start(
        [
            "beat",
            "--loglevel=info",
            "--scheduler=django_celery_beat.schedulers:DatabaseScheduler",
        ]
    )
