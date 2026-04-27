import httpx
import re
import json
from fastapi import HTTPException, status
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from .build_user_prompt import _build_user_prompt
from .create_profile_by_resume import CREATE_PROFILE_BY_RESUME_PROMPT
from app.core.logger import logger
from app.utils.sarvam_const import RESUME_GEN_TIMEOUT, SARVAM_API_URL


def _extract_json_from_text(text: str) -> str:
    """
    Robustly extract a JSON object string from LLM output.

    Strategy:
    1. Strip markdown code fences (```json ... ``` or ``` ... ```)
    2. Find the first '{' and walk the string tracking brace depth to find
       the matching '}'. This is safer than a greedy regex because it handles
       any trailing text the model appended after the closing brace.
    """
    clean = text.strip()

    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```\s*$", "", clean)
    clean = clean.strip()

    start = clean.find("{")
    if start == -1:
        raise ValueError("No '{' found in LLM output")

    depth = 0
    in_string = False
    escape_next = False
    end = -1

    for i, ch in enumerate(clean[start:], start=start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        raise ValueError("Unbalanced braces — could not find closing '}'")

    return clean[start : end + 1]


def _repair_json(json_str: str) -> str:
    """
    Apply lightweight repairs for common LLM JSON mistakes:
    - Trailing commas before ] or }
    - Single-quoted strings (replace with double quotes carefully)
    - Unquoted null/true/false that appear as bare Python values
    """
    repaired = re.sub(r",\s*([}\]])", r"\1", json_str)
    return repaired


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
        logger.debug(f"Sarvam raw response: {json.dumps(data)}")
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
    logger.debug(f"[SARVAM MESSAGE CONTENT]:\n{message_content[:3000]}")

    try:
        json_str = _extract_json_from_text(message_content)
    except ValueError as e:
        logger.error(
            f"Could not locate JSON object in Sarvam content. "
            f"Extraction error: {e}. "
            f"First 500 chars of content: {message_content[:500]}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service did not return valid JSON.",
        )

    logger.debug(f"[EXTRACTED JSON STRING (first 500)]:\n{json_str[:500]}")

    try:
        parsed_json = json.loads(json_str)
    except json.JSONDecodeError as first_err:
        logger.warning(
            f"Initial JSON parse failed at pos {first_err.pos}: {first_err.msg}. "
            f"Context: ...{json_str[max(0, first_err.pos - 80): first_err.pos + 80]}... "
            f"Attempting repair."
        )
        repaired = _repair_json(json_str)
        try:
            parsed_json = json.loads(repaired)
            logger.info("JSON parsed successfully after repair.")
        except json.JSONDecodeError as second_err:
            logger.error(
                f"JSON decode still failed after repair at pos {second_err.pos}: {second_err.msg}. "
                f"Context: ...{repaired[max(0, second_err.pos - 80): second_err.pos + 80]}..."
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Resume parsing service returned malformed JSON. Please try again.",
            )

    logger.info(
        f"Sarvam resume parsing successful. Top-level keys: {list(parsed_json.keys())}"
    )
    return parsed_json
