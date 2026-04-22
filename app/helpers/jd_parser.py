import requests
import json
import re
from app.core.logger import logger
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from app.utils.sarvam_const import MAX_TOKENS, JD_PARSE_TIMEOUT, SARVAM_API_URL


def parse_jd_with_ai(raw_jd: str) -> dict:

    prompt = f"""Parse the following job description and extract structured data. Return ONLY valid JSON with these fields (use null for missing values):
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

    headers = sarvam_api_key_headers()

    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": "You are a JSON extractor. Return ONLY valid JSON. No markdown, no explanation, no code fences.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.2,
    }

    logger.debug(f"Calling Sarvam AI API for JD parsing")

    response = requests.post(
        SARVAM_API_URL,
        json=payload,
        headers=headers,
        timeout=JD_PARSE_TIMEOUT,
    )

    response.raise_for_status()

    response_data = response.json()

    if "choices" not in response_data or len(response_data["choices"]) == 0:
        logger.error(
            "Invalid API response: No choices in response",
            extra={"response": response_data},
        )
        raise ValueError("Invalid response from AI API")

    message_content = response_data["choices"][0].get("message", {}).get("content", "")

    if not message_content:
        logger.error(
            "Invalid API response: No message content",
            extra={"response": response_data},
        )
        raise ValueError("No content in API response")

    clean = message_content.strip()
    if clean.startswith("```"):
        clean = re.sub(r"```(?:json)?\n?", "", clean).strip().rstrip("```").strip()
    parsed_json = json.loads(clean)

    logger.debug(
        f"Successfully parsed JD with AI",
        extra={"parsed_data": parsed_json},
    )

    return parsed_json
