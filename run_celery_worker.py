from app.core.celery_app import celery_app
from app.core.logger import logger

# Import tasks to register them with Celery - MUST be before worker_main
import app.tasks.ai_tasks  # Explicitly import to ensure tasks are registered

if __name__ == "__main__":
    logger.info("Starting Celery Worker...")
    logger.info(f"Registered tasks: {list(celery_app.tasks.keys())}")
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--max-tasks-per-child=100",
        ]
    )
