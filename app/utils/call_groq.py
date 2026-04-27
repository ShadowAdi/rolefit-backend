import re
import json
from fastapi import HTTPException, status
from app.helpers.grok_ai_headers import grok_api_key_headers
from .build_user_prompt import _build_user_prompt
from .create_profile_by_resume import CREATE_PROFILE_BY_RESUME_PROMPT
from app.core.logger import logger
from groq import Groq


def _extract_clean_json(text: str) -> dict:
    """Extract clean JSON from Groq response."""
    # Strip <think> blocks (reasoning models)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Strip markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"\s*```$", "", text).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract valid JSON from model output")


def _call_groq(resume_text: str, extracted_links: list[str]) -> dict:
    api_key = grok_api_key_headers()
    groq_client = Groq(api_key=api_key)

    logger.info("Calling Groq API for resume parsing")

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": CREATE_PROFILE_BY_RESUME_PROMPT,
                },
                {
                    "role": "user",
                    "content": _build_user_prompt(resume_text, extracted_links),
                },
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.1,
        )
    except Exception as e:
        logger.error(f"Groq API error during resume parsing: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service error. Please try again.",
        )

    message_content = chat_completion.choices[0].message.content

    if not message_content or not message_content.strip():
        logger.error("Groq returned empty message content")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service returned empty content.",
        )

    logger.info(f"Groq message content length: {len(message_content)} chars")
    logger.debug(f"[GROQ MESSAGE CONTENT]:\n{message_content[:3000]}")

    try:
        parsed_json = _extract_clean_json(message_content)
    except ValueError as e:
        logger.error(
            f"Could not extract JSON from Groq content. "
            f"Extraction error: {e}. "
            f"First 500 chars of content: {message_content[:500]}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service did not return valid JSON.",
        )

    logger.info(
        f"Groq resume parsing successful. Top-level keys: {list(parsed_json.keys())}"
    )
    return parsed_json
