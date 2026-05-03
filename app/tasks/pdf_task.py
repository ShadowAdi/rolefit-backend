import json
import base64
import os
from sqlalchemy.orm import Session
from app.db import db as db_module
from app.schema.pdf_resume import ResumeData

from app.helpers.build_pdf import build_pdf
from app.helpers.build_pdf_bold import build_pdf_bold
from app.helpers.build_pdf_minimalist import build_pdf_minimalist
from app.helpers.build_pdf_sidebar import build_pdf_sidebar
from app.helpers.redis_cache_helpers import set_cache
from app.models.GeneratedDocument import GeneratedDocumment
from app.core.celery_app import celery_app
from app.core.logger import logger
from app.websockets.redis_subscriber import publish_event_sync

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def _push_event(
    userId: str,
    docId: str,
    event_type: str,
    status: str,
    message: str,
    error: str = None,
):
    event = {
        "user_id": userId,
        "doc_id": docId,
        "type": event_type,
        "status": status,
        "message": message,
    }

    if error:
        event["error"] = error
    try:
        publish_event_sync(redis_url=REDIS_URL, event=event)
    except Exception as e:
        logger.warning(f"[WS event] Failed to publish: {e}")


def _get_session() -> Session:
    db_module.init_db_sync()
    if db_module.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None")
    return db_module.SessionLocal()


@celery_app.task(
    name="app.tasks.pdf_task.generate_resume_pdf",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def generate_resume_pdf(self, docId: str, userId: str, resume_type: str):
    """Generate resume PDF in background task. Returns base64-encoded PDF."""
    logger.info(
        f"[resume] Task started - doc={docId} user={userId} resume_type={resume_type}"
    )
    db = _get_session()

    try:
        logger.info(
            f"PDF generation started | user={userId} doc={docId} type={resume_type}"
        )

        doc = (
            db.query(GeneratedDocumment).filter(GeneratedDocumment.id == docId).first()
        )
        if not doc:
            raise ValueError(f"Document {docId} not found")

        if str(doc.userId) != str(userId):
            raise PermissionError(f"User {userId} does not own document {docId}")

        raw = doc.resume_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        resume_data = ResumeData(**parsed)

        pdf_cache_key = f"resume-pdf-{docId}-{resume_type}"

        try:
            if resume_type == "minimalist":
                pdf_bytes = build_pdf_minimalist(resume_data)
            elif resume_type == "bold":
                pdf_bytes = build_pdf_bold(resume_data)
            elif resume_type == "two-column":
                pdf_bytes = build_pdf_sidebar(resume_data)
            else:
                pdf_bytes = build_pdf(resume_data)

            logger.info(f"PDF generated successfully | doc={docId} type={resume_type}")

        except Exception as e:
            logger.error(f"PDF build failed for doc={docId}: {e}", exc_info=True)
            raise

        pdf_b64 = base64.b64encode(pdf_bytes).decode()
        set_cache_sync(pdf_cache_key, pdf_b64, ttl=86400)

        return {
            "status": "completed",
            "docId": docId,
            "resumeType": resume_type,
            "pdf_b64": pdf_b64,
        }

    except (ValueError, PermissionError) as e:
        logger.error(f"[resume] Validation failed doc={docId}: {e}")
        return {"status": "failed", "docId": docId, "error": str(e)}

    except Exception as exc:
        db.rollback()
        logger.error(f"[resume] Failed doc={docId}: {exc}", exc_info=True)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"[resume] Max retries exceeded doc={docId}")
            return {"status": "failed", "docId": docId, "error": "Max retries exceeded"}

    finally:
        db.close()


def set_cache_sync(key: str, value: str, ttl: int) -> None:
    """Synchronous cache setter for use in Celery tasks."""
    import asyncio
    from app.db import redis_db

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import redis

            r = redis.Redis.from_url(redis_db.REDIS_URL)
            r.setex(key, ttl, value)
        else:
            loop.run_until_complete(set_cache(key, value, ttl))
    except RuntimeError:
        import redis

        r = redis.Redis.from_url(redis_db.REDIS_URL)
        r.setex(key, ttl, value)
