import requests
import json
import re
from app.core.logger import logger
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from app.utils.sarvam_const import JD_PARSE_MAX_TOKENS, JD_PARSE_TIMEOUT, SARVAM_API_URL


class JDParseError(ValueError):
    """Raised when an LLM response cannot be parsed into the expected JD JSON."""


def _strip_think_block(text: str) -> str:
    think_open = text.find("<think>")
    if think_open == -1:
        return text

    think_close = text.find("</think>", think_open)
    if think_close != -1:
        after = text[think_close + len("</think>") :]
    else:
        after = text[think_open + len("<think>") :]

    return after.strip()


def _extract_json_from_text(text: str) -> str:
    clean = _strip_think_block(text)

    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```\s*$", "", clean)
    clean = clean.strip()

    start = clean.find("{")
    if start == -1:
        raise JDParseError("No '{' found in AI output")

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
        raise JDParseError("Unbalanced braces in AI output")

    return clean[start : end + 1]


def _repair_json(json_str: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", json_str)


def parse_jd_with_ai(raw_jd: str) -> dict:
    logger.debug("Entered parse_jd_with_ai")

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

    headers = sarvam_api_key_headers()

    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": "You are a JSON extractor. Output ONLY a single JSON object that matches the schema. Do not output <think> blocks, markdown, or any extra text.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": JD_PARSE_MAX_TOKENS,
        "temperature": 0.0,
    }

    logger.debug(f"Calling Sarvam AI API for JD parsing")

    logger.debug("Calling Sarvam AI API for JD parsing")

    response = requests.post(
        SARVAM_API_URL,
        json=payload,
        headers=headers,
        timeout=JD_PARSE_TIMEOUT,
    )

    response.raise_for_status()

    response_data = response.json()

    logger.debug(f"API response: {response_data}")

    if "choices" not in response_data or len(response_data["choices"]) == 0:
        logger.error(
            "Invalid API response: No choices in response",
            extra={"response": response_data},
        )
        raise ValueError("Invalid response from AI API")

    message_content = response_data["choices"][0].get("message", {}).get("content", "")
    finish_reason = response_data["choices"][0].get("finish_reason")

    if not message_content:
        logger.error(
            "Invalid API response: No message content",
            extra={"response": response_data},
        )
        raise ValueError("No content in API response")

    if finish_reason == "length":
        logger.warning(
            "Sarvam output hit max_tokens while parsing JD",
            extra={"max_tokens": JD_PARSE_MAX_TOKENS},
        )

    try:
        json_str = _extract_json_from_text(message_content)
        try:
            parsed_json = json.loads(json_str)
        except json.JSONDecodeError as first_err:
            logger.warning(
                f"JD JSON decode failed at pos {first_err.pos}: {first_err.msg}. Attempting repair."
            )
            repaired = _repair_json(json_str)
            parsed_json = json.loads(repaired)
    except JDParseError:
        raise
    except Exception as e:
        raise JDParseError(str(e)) from e

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
