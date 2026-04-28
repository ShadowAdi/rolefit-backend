import json
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.dependency.dependencies import get_db, get_current_user
from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.pdf_resume import ResumeData
from app.helpers.buid_cover_letter_pdf import build_cover_letter_pdf
from app.core.logger import logger

router = APIRouter(prefix="", tags=["Cover letter PDF"])


def _get_verified_doc(docId: str, userId: str, db: Session) -> GeneratedDocumment:
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

    return doc


def _parse_cover_letter_text(resume_text: str) -> ResumeData:
    try:
        raw = resume_text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(raw)
        return ResumeData(**parsed)

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse cover letter text as JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The stored cover letter content is not valid JSON. "
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
    cover_letter_data = _parse_cover_letter_text(doc.resume_text)

    try:
        pdf_bytes = build_cover_letter_pdf(cover_letter_data)
    except Exception as e:
        logger.error(f"Cover letter build failed for doc={docId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Please try again.",
        )

    name_slug = cover_letter_data.header.name.replace(" ", "_").lower()
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
    resume_data = _parse_cover_letter_text(doc.resume_text)

    try:
        pdf_bytes = build_cover_letter_pdf(resume_data)
    except Exception as e:
        logger.error(f"PDF build failed for doc={docId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Please try again.",
        )

    return _stream_pdf(pdf_bytes, "cover_letter_preview.pdf", inline=True)
