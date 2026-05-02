#!/usr/bin/env python
"""
Run Celery Worker
Execute: python run_celery_worker.py
"""

from app.celery_app import celery_app
from app.core.logger import logger
import os

if __name__ == "__main__":
    logger.info("Starting Celery Worker...")

    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=4",  # Number of concurrent tasks
            "--max-tasks-per-child=100",  # Restart worker after 100 tasks
        ]
    )
