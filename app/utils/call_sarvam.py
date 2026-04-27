import httpx
import re
import json
from fastapi import HTTPException, status
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from .build_user_prompt import _build_user_prompt
from .create_profile_by_resume import CREATE_PROFILE_BY_RESUME_PROMPT
from app.core.logger import logger
from app.utils.sarvam_const import RESUME_GEN_TIMEOUT, SARVAM_API_URL


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

    data = None
    message_content = ""

    try:
        data = response.json()

        # Log the FULL raw response so you can see exactly what Sarvam returned
        logger.debug(f"Sarvam raw response: {json.dumps(data)}")
        print(f"[SARVAM RAW RESPONSE]: {json.dumps(data, indent=2)}")

    except Exception as e:
        logger.error(
            f"Failed to parse Sarvam HTTP response as JSON: {e}. "
            f"Raw body: {response.text[:1000]}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service returned non-JSON response.",
        )

    try:
        message_content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        logger.error(
            f"Sarvam response missing expected fields. "
            f"Keys present: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}. "
            f"Error: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response structure from resume parsing service.",
        )

    if not message_content or not message_content.strip():
        logger.error("Sarvam returned empty message content")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service returned empty content.",
        )

    logger.info(f"Sarvam message content length: {len(message_content)} chars")
    print(f"[SARVAM MESSAGE CONTENT]:\n{message_content[:2000]}")

    clean = message_content.strip()

    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
        clean = clean.strip()

    # Find the outermost { ... } block
    match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
    if not match:
        logger.error(
            f"No JSON object found in Sarvam content. "
            f"First 500 chars: {clean[:500]}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service did not return valid JSON.",
        )

    json_str = match.group()
    print(f"[EXTRACTED JSON STRING FIRST 500]:\n{json_str[:500]}")

    try:
        parsed_json = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(
            f"JSON decode failed: {e}. "
            f"Problematic string around pos {e.pos}: "
            f"...{json_str[max(0, e.pos - 50): e.pos + 50]}..."
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service returned malformed JSON. Please try again.",
        )

    logger.info("Sarvam resume parsing successful")
    print(f"[PARSED JSON KEYS]: {list(parsed_json.keys())}")

    return parsed_json
