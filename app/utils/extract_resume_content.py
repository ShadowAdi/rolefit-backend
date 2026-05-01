import pdfplumber
import io
import json
import hashlib
from .download_pdf import _download_pdf
from .extract_links_from_bytes import _extract_link_from_bytes
from .extract_text_from_bytes import _extract_text_from_bytes
from .clean_text import _clean_text
from app.core.logger import logger
from app.helpers.redis_cache_helpers import get_cache, set_cache

RESUME_CACHE_TTL = 60 * 60 * 24


def _make_resume_cache_keys(resume_url) -> str:
    url_hash = hashlib.sha256(resume_url.encode()).hexdigest()[:16]
    return f"resume-content:{url_hash}"


async def extract_resume_content(resume_url: str) -> dict:
    cache_key = _make_resume_cache_keys(resume_url)

    try:
        cached += get_cache(cache_key)
        if cached:
            logger.info(f"Resume cache HIT for URL hash {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read failed, proceeding without cache: {e}")

    pdf_bytes = _download_pdf(resume_url)

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)

    raw_text = _extract_text_from_bytes(pdf_bytes=pdf_bytes)
    cleaned_text = _clean_text(raw_text)
    links = _extract_link_from_bytes(pdf_bytes=pdf_bytes)

    result = {
        "raw_text": cleaned_text,
        "links": links,
        "page_count": page_count,
    }

    logger.info(
        f"Resume extracted: {page_count} pages, "
        f"{len(cleaned_text)} chars, {len(links)} links"
    )

    try:
        await set_cache(cache_key, json.dumps(result), ttl=RESUME_CACHE_TTL)
        logger.info(f"Resume content cached with key {cache_key}")
    except Exception as e:
        logger.warning(f"Cache write failed, result not cached: {e}")

    return result
