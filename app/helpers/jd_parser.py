import json
from fastapi import HTTPException, status
from app.core.logger import logger
from app.helpers.grok_ai_headers import grok_api_key_headers
from groq import Groq
from app.utils.extract_clean_json_content import _extract_clean_json
from sqlalchemy.orm import Session
from app.models.ApiKeys import ProviderType
from typing import Optional
from app.utils.llm_helper import LLMHelper


class JDParseError(ValueError):
    """Raised when an LLM response cannot be parsed into the expected JD JSON."""


async def parse_jd_with_ai(
    db: Session, user_id: str, raw_jd: str, provider: Optional[ProviderType] = None
) -> dict:
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

    llm_helper = LLMHelper(db, user_id, provider)

    try:
        parsed_json = await llm_helper.call_with_json_response(
            prompt=prompt,
            system_prompt="You are a JSON-only job description parser. Output ONLY valid JSON.",
            max_tokens=600,
            temperature=0.1,
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

    except Exception as e:
        logger.error(f"Groq API error during resume parsing: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume parsing service error. Please try again.",
        )
