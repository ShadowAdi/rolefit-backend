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


def mark_processing(db: Session, doc_id: str):
    doc = db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
    if doc:
        doc.status = "processing"
        db.commit()


def _mark_field(db, doc_id: str, error: str):
    doc = db.query(GeneratedDocumment).filter(GeneratedDocumment.id == doc_id).first()
    if doc:
        doc.status = "failed"
        doc.error = error[:500]
        db.commit()
