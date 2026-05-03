"""
Shared helper functions for PDF operations used by both routers and tasks.
"""

import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.pdf_resume import ResumeData
from app.schema.CoverLetterData import CoverLetterData
from app.helpers.redis_cache_helpers import get_cache, set_cache
from app.core.logger import logger


async def get_verified_doc(docId: str, userId: str, db: Session) -> GeneratedDocumment:
    """Verify document ownership with caching."""
    cache_key = f"doc-owner-{docId}"
    cached_owner = await get_cache(cache_key)
    if cached_owner:
        cached_user_id = json.loads(cached_owner).get("userId")
        if str(cached_user_id) != str(userId):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this document.",
            )

    doc = db.query(GeneratedDocumment).filter(GeneratedDocumment.id == docId).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated document not found.",
        )

    if str(doc.userId) != str(userId):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document.",
        )

    await set_cache(cache_key, json.dumps({"userId": str(doc.userId)}), ttl=3600)
    return doc


async def parse_resume_text(resume_text: str, docId: str) -> ResumeData:
    """Parse and cache resume JSON data."""
    cache_key = f"resume-parsed-{docId}"
    cached_resume = await get_cache(cache_key)
    if cached_resume:
        return ResumeData(**json.loads(cached_resume))

    try:
        raw = resume_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        resume_data = ResumeData(**parsed)

        await set_cache(cache_key, json.dumps(parsed), ttl=86400)

        return resume_data

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse resume_text as JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The stored resume content is not valid JSON. "
                "Please regenerate the document."
            ),
        )


async def parse_cover_letter_text(
    cover_letter_text: str, docId: str
) -> CoverLetterData:
    """Parse and cache cover letter JSON data."""
    cache_key = f"cover-letter-parsed-{docId}"
    cached_cover_letter = await get_cache(cache_key)
    if cached_cover_letter:
        return CoverLetterData(**json.loads(cached_cover_letter))

    try:
        raw = cover_letter_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        cover_letter_data = CoverLetterData(**parsed)

        await set_cache(cache_key, json.dumps(parsed), ttl=86400)

        return cover_letter_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse cover letter text as JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The stored cover letter content is not valid JSON. "
                "Please regenerate the document."
            ),
        )
    except ValueError as e:
        logger.error(f"Failed to validate cover letter data against schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The cover letter content doesn't match the expected format. "
                "Please regenerate the document."
            ),
        )
