import base64

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import io

from sqlalchemy.orm import Session

from app.dependency.dependencies import get_db, get_current_user
from app.helpers.build_pdf import build_pdf
from app.helpers.pdf_helpers import get_verified_doc, parse_resume_text
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache
from app.tasks.pdf_task import generate_resume_pdf
from app.response.base import APIResponse

from app.core.logger import logger

router = APIRouter(prefix="", tags=["Resume PDF"])


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
async def download_resume_pdf(
    docId: str,
    resume_type: str = "classic",
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the resume as a PDF file.

    Query Parameters:
        resume_type: Type of resume template - "classic", "minimalist", "bold", or "two-column" (default: "classic")
    """
    user_id = str(current_user.id)
    logger.info(
        f"PDF download requested | user={user_id} doc={docId} type={resume_type}"
    )

    doc = await get_verified_doc(docId, user_id, db)
    resume_data = await parse_resume_text(doc.resume_text, docId)

    name_slug = resume_data.header.name.replace(" ", "_").lower()
    filename = f"{name_slug}_resume.pdf"

    pdf_cache_key = f"resume-pdf-{docId}-{resume_type}"
    cached_pdf = await get_cache(pdf_cache_key)

    if cached_pdf:
        logger.info(f"PDF served from cache | doc={docId} type={resume_type}")
        pdf_bytes = base64.b64decode(cached_pdf)
        return _stream_pdf(pdf_bytes, filename, inline=False)

    task = generate_resume_pdf.delay(
        docId=docId,
        userId=user_id,
        resume_type=resume_type,
    )

    logger.info(f"PDF generation queued | task_id={task.id} doc={docId}")

    try:
        result = task.get(timeout=60)

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
        logger.error(f"PDF generation failed | task_id={task.id} error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Please try again.",
        )


@router.get("/{docId}/preview")
async def preview_resume_pdf(
    docId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview the resume PDF inline in the browser."""
    user_id = str(current_user.id)
    logger.info(f"PDF preview requested | user={user_id} doc={docId}")

    doc = await get_verified_doc(docId, user_id, db)
    resume_data = await parse_resume_text(doc.resume_text, docId)

    # Try cache first for preview PDF
    pdf_cache_key = f"resume-pdf-{docId}-preview"
    cached_pdf = await get_cache(pdf_cache_key)
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
        await set_cache(pdf_cache_key, base64.b64encode(pdf_bytes).decode(), ttl=86400)

    return _stream_pdf(pdf_bytes, "resume_preview.pdf", inline=True)


@router.get("/{docId}/status", response_model=APIResponse)
async def get_pdf_generation_status(
    docId: str,
    task_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check the status of a PDF generation task.

    Query Parameters:
        task_id: The Celery task ID from the initial request
    """
    user_id = str(current_user.id)

    await get_verified_doc(docId, user_id, db)

    from app.core.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    return APIResponse(
        success=True,
        message="PDF generation status retrieved",
        status_code=200,
        data={
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.successful() else None,
        },
    )


@router.get("/templates", response_model=APIResponse)
async def list_templates():
    """Return available template IDs for the frontend to display as options."""
    templates = [
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
    return APIResponse(
        success=True,
        message="Templates retrieved",
        status_code=200,
        data={"templates": templates},
    )
