from app.core.celery_app import celery_app
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

    @staticmethod
    def wait_for_task(task_id: str, timeout: int = 3000) -> Any:
        result = AsyncResult(task_id, app=celery_app)
        try:
            return result.get(timeout=timeout)
        except Exception as e:
            logger.error(f"Error waiting for task {task_id}: {str(e)}")
            raise

    @staticmethod
    def revoke_task(task_id: str) -> bool:
        try:
            celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task {task_id}: {str(e)}")
            return False


class QuickTask:

    @staticmethod
    def generate_resume(user_data: dict, jd_content: str) -> str:
        return TaskHelper.submit_task(
            "app.tasks.ai_tasks.generate_resume_task", user_data, jd_content
        )

    @staticmethod
    def generate_cover_letter(user_data: Dict, jd_content: str) -> str:
        """Submit cover letter generation task and return task ID"""
        return TaskHelper.submit_task(
            "app.tasks.ai_tasks.generate_cover_letter_task", user_data, jd_content
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
