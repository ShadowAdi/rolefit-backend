import json
import base64

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import io

from sqlalchemy.orm import Session

from app.dependency.dependencies import get_db, get_current_user
from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.pdf_resume import ResumeData
from app.helpers.build_pdf import build_pdf
from app.helpers.build_pdf_bold import build_pdf_bold
from app.helpers.build_pdf_minimalist import build_pdf_minimalist
from app.helpers.build_pdf_sidebar import build_pdf_sidebar
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache

from app.core.logger import logger

router = APIRouter(prefix="", tags=["Resume PDF"])


def _get_verified_doc(docId: str, userId: str, db: Session) -> GeneratedDocumment:
    cache_key = f"doc-owner-{docId}"
    cached_owner = get_cache(cache_key)
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
    set_cache(cache_key, json.dumps({"userId": str(doc.userId)}), ttl=3600)
    return doc


def _parse_resume_text(resume_text: str, docId: str) -> ResumeData:
    # Try cache first
    cache_key = f"resume-parsed-{docId}"
    cached_resume = get_cache(cache_key)
    if cached_resume:
        return ResumeData(**json.loads(cached_resume))

    try:
        raw = resume_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        resume_data = ResumeData(**parsed)

        # Cache the parsed resume data (24 hours)
        set_cache(cache_key, json.dumps(parsed), ttl=86400)

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


@router.get("/{docId}/{resume_type}/download")
async def download_resume_pdf(
    docId: str,
    resume_type: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the resume as a PDF file."""
    user_id = str(current_user.id)
    logger.info(f"PDF download requested | user={user_id} doc={docId}")

    doc = _get_verified_doc(docId, user_id, db)
    resume_data = _parse_resume_text(doc.resume_text, docId)

    # Try cache first for PDF bytes
    pdf_cache_key = f"resume-pdf-{docId}-{resume_type}"
    cached_pdf = get_cache(pdf_cache_key)
    if cached_pdf:
        logger.info(f"PDF served from cache | doc={docId} type={resume_type}")
        pdf_bytes = base64.b64decode(cached_pdf)
    else:
        try:
            if resume_type == "minimalist":
                pdf_bytes = build_pdf_minimalist(resume_data)
            elif resume_type == "bold":
                pdf_bytes = build_pdf_bold(resume_data)
            elif resume_type == "two-column":
                pdf_bytes = build_pdf_sidebar(resume_data)
            else:
                pdf_bytes = build_pdf(resume_data)

        except Exception as e:
            logger.error(f"PDF build failed for doc={docId}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please try again.",
            )

        # Cache the PDF bytes (24 hours)
        set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    name_slug = resume_data.header.name.replace(" ", "_").lower()
    return _stream_pdf(pdf_bytes, f"{name_slug}_resume.pdf", inline=False)


@router.get("/{docId}/preview")
async def preview_resume_pdf(
    docId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview the resume PDF inline in the browser."""
    user_id = str(current_user.id)
    logger.info(f"PDF preview requested | user={user_id} doc={docId}")

    doc = _get_verified_doc(docId, user_id, db)
    resume_data = _parse_resume_text(doc.resume_text, docId)

    # Try cache first for preview PDF
    pdf_cache_key = f"resume-pdf-{docId}-preview"
    cached_pdf = get_cache(pdf_cache_key)
    if cached_pdf:
        logger.info(f"PDF preview served from cache | doc={docId}")
        pdf_bytes = base64.b64decode(cached_pdf)
    else:
        try:
            pdf_bytes = build_pdf(resume_data)
        except Exception as e:
            logger.error(f"PDF build failed for doc={docId}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please try again.",
            )

        # Cache the preview PDF (24 hours)
        set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    return _stream_pdf(pdf_bytes, "resume_preview.pdf", inline=True)


@router.get("/templates")
async def list_templates():
    """Return available template IDs for the frontend to display as options."""
    return {
        "templates": [
            {
                "id": "classic",
                "name": "Classic",
                "description": "Clean single-column layout with accent-coloured headings.",
            },
            {
                "id": "minimalist",
                "name": "Minimalist",
                "description": "Generous white space, thin rules, muted tones — very readable.",
            },
            {
                "id": "bold",
                "name": "Bold",
                "description": "Dark header block, vivid accent sidebar rules — stands out.",
            },
        ]
    }
