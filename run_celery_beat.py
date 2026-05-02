#!/usr/bin/env python
"""
Run Celery Beat Scheduler
This runs periodic tasks (like cleanup tasks that run every hour)
Execute: python run_celery_beat.py
"""

from app.celery_app import celery_app
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
