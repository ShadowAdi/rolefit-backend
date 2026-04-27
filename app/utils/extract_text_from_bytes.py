import pdfplumber
import io
from app.core.logger import logger
from fastapi import HTTPException, status


def _extract_text_from_bytes(pdf_bytes: bytes) -> str:
    raw_pages: list[str] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if len(pdf.pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded PDF appears to be empty (0 pages).",
            )

        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text(x_tolerance=2, y_tolerance=4) or ""
            raw_pages.append(page_text)

    full_text = "\n\n".join(raw_pages)

    if not full_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No extractable text found in the PDF. "
                "The file may be a scanned image. "
                "Please upload a text-based PDF."
            ),
        )

    return full_text
