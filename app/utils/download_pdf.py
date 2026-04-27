import httpx
from .normalise_url import _normalise_url
from app.core.logger import logger
from fastapi.exceptions import HTTPException
from fastapi import status


def _download_pdf(url: str) -> bytes:
    direct_url = _normalise_url(url=url)
    logger.info(f"Downloading resume PDF from: {direct_url}")

    try:
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(direct_url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        if "text/html" in content_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "The URL returned an HTML page instead of a PDF. "
                    "If this is a Google Drive link, make sure sharing is set to "
                    "'Anyone with the link' and the file is under 25 MB."
                ),
            )

        if "pdf" not in content_type and not direct_url.lower().endswith(".pdf"):
            logger.warning(
                f"Unexpected content-type '{content_type}' for URL {direct_url}"
            )

        return response.content

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out while downloading the resume PDF. Please try again.",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to download resume PDF: HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network error while downloading resume PDF: {str(e)}",
        )
