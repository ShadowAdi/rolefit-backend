import json
import base64
import io

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from typing import Literal


from app.dependency.dependencies import get_db, get_current_user
from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.CoverLetterData import CoverLetterData
from app.helpers.buid_cover_letter_pdf import build_cover_letter_pdf
from app.helpers.build_cover_letter_bold import build_cover_letter_pdf_bold
from app.helpers.build_cover_letter_minimal import build_cover_letter_pdf_minimal
from app.helpers.pdf_helpers import get_verified_doc, parse_cover_letter_text
from app.helpers.redis_cache_helpers import get_cache, set_cache
from app.tasks.cover_letter_task import generate_cover_letter_pdf
from app.core.logger import logger

router = APIRouter(prefix="", tags=["Cover letter PDF"])


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
    cover_letter_type: str = Query(
        default="classic",
        description="Cover letter template: classic, bold, or minimal",
    ),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the cover letter as a PDF file."""
    user_id = str(current_user.id)
    logger.info(
        f"Cover letter PDF download requested | user={user_id} doc={docId} type={cover_letter_type}"
    )

    # Verify document access first
    doc = await get_verified_doc(docId, user_id, db)
    cover_letter_data = await parse_cover_letter_text(doc.cover_letter_text, docId)

    # Get filename from candidate name
    name_slug = cover_letter_data.candidate.name.replace(" ", "_").lower()
    filename = f"{name_slug}_cover_letter.pdf"

    # Check cache first
    pdf_cache_key = f"cover-letter-pdf-{docId}-{cover_letter_type}"
    cached_pdf = await get_cache(pdf_cache_key)

    if cached_pdf:
        logger.info(
            f"Cover letter PDF served from cache | doc={docId} type={cover_letter_type}"
        )
        pdf_bytes = base64.b64decode(cached_pdf)
        return _stream_pdf(pdf_bytes, filename, inline=False)

    # Trigger async task to generate PDF
    task = generate_cover_letter_pdf.delay(
        docId=docId,
        userId=user_id,
        cover_letter_type=cover_letter_type,
    )

    logger.info(f"Cover letter PDF generation queued | task_id={task.id} doc={docId}")

    # Wait for task completion with timeout (adjust as needed)
    try:
        result = task.get(timeout=60)  # 60 second timeout

        if result.get("status") == "completed":
            pdf_b64 = result.get("pdf_b64")
            pdf_bytes = base64.b64decode(pdf_b64)
            return _stream_pdf(pdf_bytes, filename, inline=False)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF generation failed: {result.get('error', 'Unknown error')}",
            )
    except Exception as e:
        logger.error(
            f"Cover letter PDF generation failed | task_id={task.id} error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Please try again.",
        )


@router.get("/{docId}/preview")
async def preview_cover_letter_pdf(
    docId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview the cover letter PDF inline in the browser."""
    user_id = str(current_user.id)
    logger.info(f"Cover letter PDF preview requested | user={user_id} doc={docId}")

    doc = await get_verified_doc(docId, user_id, db)
    cover_letter_data = await parse_cover_letter_text(doc.cover_letter_text, docId)

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
            logger.error(
                f"Cover letter PDF build failed for doc={docId}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please try again.",
            )

        # Cache the preview PDF (24 hours)
        await set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    return _stream_pdf(pdf_bytes, "cover_letter_preview.pdf", inline=True)


@router.get("/{docId}/status")
async def get_cover_letter_pdf_generation_status(
    docId: str,
    task_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check the status of a cover letter PDF generation task.

    Query Parameters:
        task_id: The Celery task ID from the initial request
    """
    user_id = str(current_user.id)

    # Verify document access
    await get_verified_doc(docId, user_id, db)

    from app.core.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.successful() else None,
    }


@router.get("/templates")
async def list_cl_templates():
    """Return available cover letter template options for the frontend."""
    return {
        "templates": [
            {
                "id": "classic",
                "name": "Classic",
                "description": "Centered accent name, thin rule, clean body.",
            },
            {
                "id": "bold",
                "name": "Bold",
                "description": "Dark navy header, red-pink accent bars, strong typography.",
            },
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Left-aligned, no rule, wide margins, airy spacing.",
            },
        ]
    }
