import json
from uuid import UUID
from datetime import datetime, timedelta, timezone

from celery import shared_task
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from groq import Groq

from celery_app import celery_app
from app.helpers.grok_ai_headers import grok_api_key_headers
from app.utils.extract_clean_json_content import _extract_clean_json
from app.db.db import SessionLocal
from app.helpers.filter_jd_sync import filter_jd_sync
from app.models.GeneratedDocument import GeneratedDocumment
from app.utils.prompt_utils import _extract_clean_json
from app.helpers.resume_prompt import build_resume_prompt
from app.helpers.cover_letter_prompt import _build_cover_letter_prompt
from app.helpers.filter_jd import filter_jd_sync
from app.core.logger import logger
from app.core.grok_const import GROQ_MAX_TOKENS, GROQ_MODEL, GROQ_TEMP


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
    db = SessionLocal()
    try:
        _mark_processing(db, doc_id)
        job_profile = filter_jd_sync(
            job_id=job_id, user_id=user_id, db=db, content_type="Resume"
        )
        prompt = build_resume_prompt(job_profile, user_specifications)
        clean_json = _call_groq(prompt)

        doc = (
            db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
        )
        if not doc:
            raise ValueError(f"Doc {doc_id} not found in DB")

        doc.resume_text = json.dumps(clean_json)
        doc.status = "completed"
        db.commit()

        logger.info(f"[resume] Completed doc={doc_id}")
        return {"status": "completed", "doc_id": doc_id}
    except Exception as exc:
        db.rollback()
        logger.error(f"[resume] Failed doc={doc_id}: {exc}", exc_info=True)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _mark_failed(db, doc_id, str(exc))
            logger.error(f"[resume] Max retries exceeded doc={doc_id}")
            return {"status": "failed", "doc_id": doc_id}

    finally:
        db.close()


@celery_app.task(name="app.tasks.ai_tasks.cleanup_old_tasks")
def cleanup_old_tasks():
    db = SessionLocal()
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
        return {"cleaned": len(stuck)}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"[cleanup] DB error: {e}")
    finally:
        db.close()
