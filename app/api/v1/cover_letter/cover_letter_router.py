import json
import base64
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.dependency.dependencies import get_db, get_current_user
from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.CoverLetterData import CoverLetterData
from app.helpers.buid_cover_letter_pdf import build_cover_letter_pdf
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache
from app.core.logger import logger

router = APIRouter(prefix="", tags=["Cover letter PDF"])


async def _get_verified_doc(docId: str, userId: str, db: Session) -> GeneratedDocumment:
    # Try cache first - only store userId for ownership verification (safe & lightweight)
    cache_key = f"doc-owner-{docId}"
    cached_owner = await get_cache(cache_key)
    if cached_owner:
        cached_user_id = json.loads(cached_owner).get("userId")
        if str(cached_user_id) != str(userId):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this document.",
            )

    # Always fetch fresh doc from DB (ensures latest data, avoids ORM serialization issues)
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

    # Cache only ownership metadata - safe, lightweight JSON (1 hour)
    await set_cache(cache_key, json.dumps({"userId": str(doc.userId)}), ttl=3600)

    return doc


async def _parse_cover_letter_text(
    cover_letter_text: str, docId: str
) -> CoverLetterData:
    # Try cache first
    cache_key = f"cover-letter-parsed-{docId}"
    cached_cover_letter = await get_cache(cache_key)
    if cached_cover_letter:
        return CoverLetterData(**json.loads(cached_cover_letter))

    try:
        raw = cover_letter_text.strip()

        # Handle markdown code blocks (```)
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        cover_letter_data = CoverLetterData(**parsed)

        # Cache the parsed cover letter data (24 hours)
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


def _stream_pdf(pdf_bytes: bytes, filename: str, inline: bool) -> StreamingResponse:
    disposition = "inline" if inline else "attachment"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'{disposition}; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get("/{docId}/download")
async def download_cover_letter_pdf(
    docId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the resume as a PDF file."""
    user_id = str(current_user.id)
    logger.info(f"PDF download requested | user={user_id} doc={docId}")

    doc = _get_verified_doc(docId, user_id, db)
    cover_letter_data = _parse_cover_letter_text(doc.cover_letter_text, docId)

    # Try cache first for PDF bytes
    pdf_cache_key = f"cover-letter-pdf-{docId}"
    cached_pdf = await get_cache(pdf_cache_key)
    if cached_pdf:
        logger.info(f"Cover letter PDF served from cache | doc={docId}")
        pdf_bytes = base64.b64decode(cached_pdf)
    else:
        try:
            pdf_bytes = build_cover_letter_pdf(cover_letter_data)
        except Exception as e:
            logger.error(
                f"Cover letter build failed for doc={docId}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please try again.",
            )

        # Cache the PDF bytes (24 hours)
        await set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    name_slug = cover_letter_data.candidate.name.replace(" ", "_").lower()
    return _stream_pdf(pdf_bytes, f"{name_slug}_cover_letter.pdf", inline=False)


@router.get("/{docId}/preview")
async def preview_cover_letter_pdf(
    docId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview the resume PDF inline in the browser."""
    user_id = str(current_user.id)
    logger.info(f"PDF preview requested | user={user_id} doc={docId}")

    doc = _get_verified_doc(docId, user_id, db)
    cover_letter_data = _parse_cover_letter_text(doc.cover_letter_text, docId)

    # Try cache first for preview PDF
    pdf_cache_key = f"cover-letter-pdf-{docId}-preview"
    cached_pdf = await get_cache(pdf_cache_key)
    if cached_pdf:
        logger.info(f"Cover letter PDF preview served from cache | doc={docId}")
        pdf_bytes = base64.b64decode(cached_pdf)
    else:
        try:
            pdf_bytes = build_cover_letter_pdf(cover_letter_data)
        except Exception as e:
            logger.error(f"PDF build failed for doc={docId}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please try again.",
            )

        # Cache the preview PDF (24 hours)
        await set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    return _stream_pdf(pdf_bytes, "cover_letter_preview.pdf", inline=True)
