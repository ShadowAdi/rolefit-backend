from celery import Celery
from app.celery_app import celery_app
from app.core.logger import logger
from celery.result import AsyncResult
from typing import Any, Dict


class TaskHelper:

    @staticmethod
    def submit_task(task_name: str, *args, **kwargs) -> str:
        try:
            task = celery_app.send_task(task_name, args=args, kwargs=kwargs)
            logger.info(f"Task submitted: {task_name} with ID: {task.id}")
            return task.id
        except Exception as e:
            logger.error(f"Failed to submit task {task_name}: {str(e)}")
            raise

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        result = AsyncResult(task_id, app=celery_app)
        if result.state == "PENDING":
            return {
                "status": "PENDING",
                "progress": "0%",
                "message": "Task is waiting to be executed",
            }

        elif result.state == "PROGRESS":
            return {
                "status": "PROGRESS",
                "progress": f"{result.info.get('progress', 0)}%",
                "message": result.info.get("message", "Processing..."),
            }

        elif result.state == "SUCCESS":
            return {"status": "SUCCESS", "result": result.result}
        elif result.state == "FAILURE":
            return {"status": "FAILURE", "error": str(result.info)}
        elif result.state == "RETRY":
            return {"status": "RETRY", "message": "Task is being retried"}
        else:
            return {"status": result.state, "info": str(result.info)}
