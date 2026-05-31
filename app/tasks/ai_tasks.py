import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from groq import Groq

from app.core.celery_app import celery_app
from app.helpers.grok_ai_headers import grok_api_key_headers
from app.db import db as db_module
from app.helpers.filter_jd_sync import filter_jd_sync
from app.models.GeneratedDocument import GeneratedDocumment
from app.utils.extract_clean_json_content import _extract_clean_json
from app.helpers.resume_prompt import build_resume_prompt
from app.helpers.cover_letter_prompt import _build_cover_letter_prompt
from app.core.logger import logger
from app.core.grok_const import GROQ_MAX_TOKENS, GROQ_MODEL, GROQ_TEMP
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
    """Get a database session for Celery tasks"""
    db_module.init_db_sync()

    if db_module.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None")

    return db_module.SessionLocal()


def _get_groq_client() -> Groq:
    return Groq(api_key=grok_api_key_headers())


def _call_groq(prompt: str) -> dict:
    client = _get_groq_client()
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a JSON-only resume writer. "
                    "Output ONLY valid JSON. No markdown, no explanation, no extra text."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        model=GROQ_MODEL,
        max_tokens=GROQ_MAX_TOKENS,
        temperature=GROQ_TEMP,
    )
    content = completion.choices[0].message.content

    if not content:
        raise ValueError("Groq returned empty content")
    return _extract_clean_json(content)


def _mark_processing(db: Session, doc_id: str):
    doc = db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
    if doc:
        doc.status = "processing"
        db.commit()


def _mark_failed(db, doc_id: str, error: str):
    doc = db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
    if doc:
        doc.status = "failed"
        doc.error = error[:500]
        db.commit()


@celery_app.task(
    name="app.tasks.ai_tasks.generate_resume_task",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def generate_resume_task(
    self, doc_id: str, user_id: str, job_id: str, user_specifications: str
):
    logger.info(f"[resume] Task started - doc={doc_id} user={user_id} job={job_id}")
    db = _get_session()
    try:
        _mark_processing(db, doc_id)
        logger.info(f"[resume] Marked as processing - doc={doc_id}")

        job_profile = filter_jd_sync(
            job_id=job_id, user_id=user_id, db=db, content_type="Resume"
        )
        logger.info(f"[resume] Got job profile - doc={doc_id}")

        prompt = build_resume_prompt(job_profile, user_specifications)
        logger.info(f"[resume] Built prompt - doc={doc_id}")

        clean_json = _call_groq(prompt)
        logger.info(f"[resume] Got response from Groq - doc={doc_id}")

        doc = (
            db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
        )
        if not doc:
            raise ValueError(f"Doc {doc_id} not found in DB")

        doc.resume_text = json.dumps(clean_json)
        doc.status = "completed"
        db.commit()

        try:
            _push_event(
                userId=user_id,
                docId=doc_id,
                event_type="generate_resume_content",
                status="completed",
                message="Your resume is ready. Choose a template to download.",
            )
        except Exception as e:
            logger.warning(f"[resume] Event push failed (non-fatal): {e}")

        logger.info(f"[resume] Completed doc={doc_id}")
        return {"status": "completed", "doc_id": doc_id}
    except Exception as exc:
        db.rollback()
        logger.error(f"[resume] Failed doc={doc_id}: {exc}", exc_info=True)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _mark_failed(db, doc_id, str(exc))
            _push_event(
                user_id=user_id,
                doc_id=doc_id,
                event_type="generate_resume_content_failed",
                status="failed",
                message="Resume generation failed. Please try again.",
                error=str(exc),
            )
            logger.error(f"[resume] Max retries exceeded doc={doc_id}")
            return {"status": "failed", "doc_id": doc_id}

    finally:
        db.close()


@celery_app.task(
    name="app.tasks.ai_tasks.generate_cover_letter_task",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def generate_cover_letter_task(
    self,
    doc_id: str,
    user_id: str,
    job_id: str,
    user_specifications: str,
):
    """
    Worker task: build cover letter content via Groq and save to DB.

    Called by: ContentService.generate_cover_letter_content()
    """
    logger.info(
        f"[cover_letter] Starting task doc={doc_id} user={user_id} job={job_id}"
    )
    db = _get_session()

    try:
        _mark_processing(db, doc_id)

        job_profile = filter_jd_sync(
            job_id=job_id, user_id=user_id, db=db, content_type="cover_letter"
        )

        prompt = _build_cover_letter_prompt(job_profile, user_specifications)
        clean_json = _call_groq(prompt)

        doc = (
            db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
        )
        if not doc:
            raise ValueError(f"Doc {doc_id} not found in DB")

        doc.cover_letter_text = json.dumps(clean_json)
        doc.status = "completed"
        db.commit()

        try:
            _push_event(
                userId=user_id,
                docId=doc_id,
                event_type="cover_letter_generation_completed",
                status="completed",
                message="Your cover letter is ready. Choose a template to download.",
            )
        except Exception as e:
            logger.warning(f"[cover_letter] Event push failed (non-fatal): {e}")

        logger.info(f"[cover_letter] Completed doc={doc_id}")
        return {"status": "completed", "doc_id": doc_id}

    except Exception as exc:
        db.rollback()
        logger.error(f"[cover_letter] Failed doc={doc_id}: {exc}", exc_info=True)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _mark_failed(db, doc_id, str(exc))
            _push_event(
                userId=user_id,
                docId=doc_id,
                event_type="cover_letter_failed",
                status="failed",
                message="Cover letter generation failed. Please try again.",
                error=str(exc),
            )
            logger.error(f"[cover_letter] Max retries exceeded doc={doc_id}")
            return {"status": "failed", "doc_id": doc_id}

    finally:
        db.close()


@celery_app.task(name="app.tasks.ai_tasks.cleanup_old_tasks")
def cleanup_old_tasks():
    db = _get_session()
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)

    try:
        stuck = (
            db.query(GeneratedDocumment)
            .filter(
                GeneratedDocumment.status == "processing",
                GeneratedDocumment.created_at < cutoff,
            )
            .all()
        )
        for doc in stuck:
            doc.status = "failed"
            doc.error = "Task timed out — please regenerate."
            logger.warning(f"[cleanup] Marked stuck doc={doc.id} as failed")
        db.commit()
        logger.info(f"[cleanup] Cleaned {len(stuck)} stuck tasks")
        _push_event(
            userId=str(doc.userId),
            docId=str(doc.id),
            event_type=(
                "resume_failed"
                if doc.gen_doc_type == "Resume"
                else "cover_letter_failed"
            ),
            status="failed",
            message="Generation timed out. Please try again.",
            error="Task timed out after 30 minutes.",
        )
        return {"cleaned": len(stuck)}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"[cleanup] DB error: {e}")
    finally:
        db.close()
