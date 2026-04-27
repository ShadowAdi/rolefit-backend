import httpx
import re
import json
from fastapi import HTTPException, status
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from .build_user_prompt import _build_user_prompt
from .create_profile_by_resume import CREATE_PROFILE_BY_RESUME_PROMPT
from app.core.logger import logger
from app.utils.sarvam_const import RESUME_GEN_TIMEOUT, SARVAM_API_URL
from app.core.logger import logger


def _call_sarvam(resume_text: str, extracted_links: list[str]) -> dict:
    headers = sarvam_api_key_headers()
    payload = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": CREATE_PROFILE_BY_RESUME_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(resume_text, extracted_links),
            },
        ],
        "max_tokens": 2000,
        "temperature": 0.1,
    }

    logger.info("Calling Sarvam API for resume parsing")

    try:
        with httpx.Client(timeout=RESUME_GEN_TIMEOUT) as client:
            response = client.post(SARVAM_API_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error("Sarvam API timed out during resume parsing")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Resume parsing timed out. Please try again.",
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Sarvam API returned error: {e.response.status_code} — {e.response.text}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Resume parsing service error: {e.response.status_code}",
        )
    except httpx.RequestError as e:
        logger.error(f"Sarvam API network error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the resume parsing service.",
        )

    try:
        data = response.json()
        message_content = data["choices"][0].get("message", {}).get("content", "")
        if not message_content:
            logger.error(
                "Invalid API response: No message content",
                extra={"response": message_content},
            )
            raise ValueError("No content in API response")
        clean = message_content.strip()
        match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in AI response")
        parsed_json = json.loads(match.group())
        print(f"after cleaning {clean}")
        logger.debug(
            "Successfully parsed JD with AI", extra={"parsed_data": parsed_json}
        )

        logger.debug(
            f"Successfully parsed JD with AI",
            extra={"parsed_data": parsed_json},
        )

        return parsed_json

    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Unexpected Sarvam response shape: {data}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response from resume parsing service.",
        )
