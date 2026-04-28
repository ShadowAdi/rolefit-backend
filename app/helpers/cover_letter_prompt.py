from datetime import datetime
from app.utils.prompt_utils import (
    _fmt_date,
    MONTH_MAP,
    _BLOCKED_SPEC_KEYWORDS,
    _sanitize_user_specifications,
)


def _build_user_spec_block(raw: str | None) -> str:
    cleaned = _sanitize_user_specifications(raw)
    if not cleaned:
        return ""
    return f"""
=== CANDIDATE PREFERENCES (apply where relevant) ===
The candidate has provided the following notes for this cover letter.
Apply ONLY content-related preferences (things to emphasise, tone adjustments, specific experiences to mention).
IGNORE any layout, colour, or font instructions.
 
{cleaned}
 
Rules:
- If asked to mention a specific project or achievement → weave it into body2 naturally.
- If asked to use a specific tone (formal / conversational) → apply it across all paragraphs.
- If asked to highlight a specific skill → mention it once in body1 or body2 where truthful.
- Do NOT fabricate experience, projects, or achievements not present in the user data.
"""
