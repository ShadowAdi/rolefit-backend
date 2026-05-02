"""
Celery Helper Functions
Makes it super easy to use Celery in your API routes
"""

from celery.result import AsyncResult
from app.celery_app import celery_app
from app.core.logger import logger
from typing import Any, Dict


class TaskHelper:
    """Simple wrapper around Celery tasks for easy usage"""

    @staticmethod
    def submit_task(task_name: str, *args, **kwargs) -> str:
        """
        Submit a task to Celery and return the task ID

        Usage:
            task_id = TaskHelper.submit_task('app.tasks.ai_tasks.generate_resume_with_ai', user_data, jd)

        Args:
            task_name: Full task name (e.g., 'app.tasks.ai_tasks.generate_resume_with_ai')
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task

        Returns:
            Task ID string that you can use to check status
        """
        try:
            task = celery_app.send_task(task_name, args=args, kwargs=kwargs)
            logger.info(f"Task submitted: {task_name} with ID: {task.id}")
            return task.id
        except Exception as e:
            logger.error(f"Failed to submit task {task_name}: {str(e)}")
            raise

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """
        Check the status of a task

        Usage:
            status = TaskHelper.get_task_status(task_id)
            print(status)  # {'status': 'SUCCESS', 'result': {...}}

        Args:
            task_id: The task ID returned from submit_task

        Returns:
            Dictionary with status and result/error
        """
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

    @staticmethod
    def wait_for_task(task_id: str, timeout: int = 300) -> Any:
        """
        Wait for a task to complete (blocking)

        Usage:
            result = TaskHelper.wait_for_task(task_id, timeout=300)

        Args:
            task_id: The task ID
            timeout: How long to wait in seconds (default 5 minutes)

        Returns:
            Task result
        """
        result = AsyncResult(task_id, app=celery_app)
        try:
            return result.get(timeout=timeout)
        except Exception as e:
            logger.error(f"Error waiting for task {task_id}: {str(e)}")
            raise

    @staticmethod
    def revoke_task(task_id: str) -> bool:
        """
        Cancel a running task

        Usage:
            TaskHelper.revoke_task(task_id)

        Args:
            task_id: The task ID

        Returns:
            True if successfully revoked
        """
        try:
            celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task {task_id}: {str(e)}")
            return False


# Quick shortcuts for common tasks
class QuickTasks:
    """Quick shortcuts to submit common tasks"""

    @staticmethod
    def generate_resume(user_data: Dict, jd_content: str) -> str:
        """Submit resume generation task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.ai_tasks.generate_resume_with_ai", user_data, jd_content
        )

    @staticmethod
    def generate_cover_letter(user_data: Dict, jd_content: str) -> str:
        """Submit cover letter generation task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.ai_tasks.generate_cover_letter_with_ai", user_data, jd_content
        )

    @staticmethod
    def generate_resume_pdf(
        user_id: str, resume_data: Dict, template: str = "default"
    ) -> str:
        """Submit resume PDF generation task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.pdf_tasks.generate_resume_pdf", user_id, resume_data, template
        )

    @staticmethod
    def generate_cover_letter_pdf(
        user_id: str, cover_letter_data: Dict, template: str = "default"
    ) -> str:
        """Submit cover letter PDF generation task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.pdf_tasks.generate_cover_letter_pdf",
            user_id,
            cover_letter_data,
            template,
        )

    @staticmethod
    def parse_jd(jd_content: str) -> str:
        """Submit JD parsing task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.ai_tasks.parse_job_description", jd_content
        )
