import json
import base64
import os
from sqlalchemy.orm import Session
from app.db import db as db_module
from app.schema.CoverLetterData import CoverLetterData

from app.helpers.buid_cover_letter_pdf import build_cover_letter_pdf
from app.helpers.build_cover_letter_bold import build_cover_letter_pdf_bold
from app.helpers.build_cover_letter_minimal import build_cover_letter_pdf_minimal
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
    name="app.tasks.cover_letter_task.generate_cover_letter_pdf",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def generate_cover_letter_pdf(self, docId: str, userId: str, cover_letter_type: str):
    """Generate cover letter PDF in background task. Returns base64-encoded PDF."""
    logger.info(
        f"[cover_letter] Task started - doc={docId} user={userId} type={cover_letter_type}"
    )
    db = _get_session()

    try:
        logger.info(
            f"Cover letter PDF generation started | user={userId} doc={docId} type={cover_letter_type}"
        )

        doc = (
            db.query(GeneratedDocumment).filter(GeneratedDocumment.id == docId).first()
        )
        if not doc:
            raise ValueError(f"Document {docId} not found")

        if str(doc.userId) != str(userId):
            raise PermissionError(f"User {userId} does not own document {docId}")

        # Notify the client that PDF generation has started
        _push_event(
            userId=userId,
            docId=docId,
            event_type="cover_letter_pdf_processing",
            status="processing",
            message="Your cover letter PDF is being generated...",
        )

        raw = doc.cover_letter_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        cover_letter_data = CoverLetterData(**parsed)

        pdf_cache_key = f"cover-letter-pdf-{docId}-{cover_letter_type}"

        try:
            if cover_letter_type == "minimalist":
                pdf_bytes = build_cover_letter_pdf_minimal(cover_letter_data)
            elif cover_letter_type == "bold":
                pdf_bytes = build_cover_letter_pdf_bold(cover_letter_data)
            else:
                pdf_bytes = build_cover_letter_pdf(cover_letter_data)

            logger.info(
                f"Cover letter PDF generated successfully | doc={docId} type={cover_letter_type}"
            )

            _push_event(
                userId=userId,
                docId=docId,
                event_type="cover_letter_pdf_generated",
                status="completed",
                message="Cover letter PDF has been generated based on chosen template.",
            )

        except Exception as e:
            logger.error(
                f"Cover letter PDF build failed for doc={docId}: {e}", exc_info=True
            )
            raise

        pdf_b64 = base64.b64encode(pdf_bytes).decode()
        set_cache_sync(pdf_cache_key, pdf_b64, ttl=86400)

        return {
            "status": "completed",
            "docId": docId,
            "coverLetterType": cover_letter_type,
            "pdf_b64": pdf_b64,
        }

    except (ValueError, PermissionError) as e:
        logger.error(f"[cover_letter] Validation failed doc={docId}: {e}")
        _push_event(
            userId=userId,
            docId=docId,
            event_type="cover_letter_pdf_error",
            status="failed",
            message="Cover letter PDF generation failed due to validation error.",
            error=str(e),
        )
        return {"status": "failed", "docId": docId, "error": str(e)}

    except Exception as exc:
        db.rollback()
        logger.error(f"[cover_letter] Failed doc={docId}: {exc}", exc_info=True)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"[cover_letter] Max retries exceeded doc={docId}")
            _push_event(
                userId=userId,
                docId=docId,
                event_type="cover_letter_pdf_error",
                status="failed",
                message="Cover letter PDF generation failed after maximum retries.",
                error="Max retries exceeded",
            )
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
