import pdfplumber
import io
from .download_pdf import _download_pdf
from .extract_links_from_bytes import _extract_link_from_bytes
from .extract_text_from_bytes import _extract_text_from_bytes
from .clean_text import _clean_text
from app.core.logger import logger


def extract_resume_content(resume_url: str) -> dict:
    pdf_bytes = _download_pdf(resume_url)

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)

    raw_text = _extract_text_from_bytes(pdf_bytes=pdf_bytes)
    cleaned_text = _clean_text(raw_text)
    links = _extract_link_from_bytes(pdf_bytes=pdf_bytes)

    logger.info(
        f"Resume extracted: {page_count} pages, "
        f"{len(cleaned_text)} chars, {len(links)} links"
    )

    return {
        "raw_text": cleaned_text,
        "links": links,
        "page_count": page_count,
    }
