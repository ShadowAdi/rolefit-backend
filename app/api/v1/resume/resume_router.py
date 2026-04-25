import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import io

from sqlalchemy.orm import Session

from app.dependency.dependencies import get_db, get_current_user
from app.models.GeneratedDocument import GeneratedDocumment
from app.schema.pdf_resume import ResumeData
from app.helpers.build_pdf import build_pdf
from app.core.logger import logger

router = APIRouter(prefix="", tags=["Resume PDF"])


def _get_verifified_doc(docId: str, userId: str, db: Session) -> GeneratedDocumment:
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
