from app.core.celery_app import celery_app
from app.core.logger import logger

# Import tasks to register them with Celery
import app.tasks  # This imports __init__.py which imports all tasks

if __name__ == "__main__":
    logger.info("Starting Celery Worker...")
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--max-tasks-per-child=100",
        ]
    )
