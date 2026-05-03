import json
from fastapi import HTTPException, status
from app.core.logger import logger
from app.helpers.grok_ai_headers import grok_api_key_headers
from groq import Groq
from app.utils.extract_clean_json_content import _extract_clean_json


class JDParseError(ValueError):
    """Raised when an LLM response cannot be parsed into the expected JD JSON."""


def parse_jd_with_ai(raw_jd: str) -> dict:
    logger.debug("Entered parse_jd_with_ai")

    api_key = grok_api_key_headers()
    groq_client = Groq(api_key=api_key)

    prompt = f"""Parse the following job description and extract structured data.

Return EXACTLY ONE JSON object (no <think>, no markdown, no code fences, no commentary).
Use null for missing values.

Schema:
{{
  "role_name": "job title",
  "company": "company name",
  "role_type": "Full-time|Internship|Contract",
  "location": "Remote|Hybrid|On-site",
  "location_city": "city name",
  "salary_min": "minimum salary or null",
  "salary_max": "maximum salary or null",
  "salary_currency": "USD|EUR|etc",
  "duration": "for internships only, e.g. 3 months",
  "tech_stack": ["technology1", "technology2"],
  "required_skills": ["skill1", "skill2"],
  "experience_required": "experience level description",
  "summary": "brief 2-3 line summary"
}}

Job Description:
{raw_jd}"""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=600,
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

    logger.debug(
        "Successfully parsed JD with AI",
        extra={
            "parsed_keys": (
                list(parsed_json.keys()) if isinstance(parsed_json, dict) else None
            )
        },
    )

    if not isinstance(parsed_json, dict):
        raise JDParseError("AI output JSON was not an object")

    return parsed_json
