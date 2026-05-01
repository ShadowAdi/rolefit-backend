from datetime import datetime
from app.utils.prompt_utils import (
    _fmt_date,
    _sanitize_user_specifications,
)

# ── Paragraph-count config ────────────────────────────────────────────────

_PARA_CONFIGS = {
    2: {
        "description": "2 paragraphs: opening + closing only (very concise).",
        "rules": (
            "opening: 3-4 sentences — combine enthusiasm AND strongest experience.\n"
            'body1:   leave as empty string "".\n'
            'body2:   leave as empty string "".\n'
            "closing: 2-3 sentences — confident call-to-action."
        ),
    },
    3: {
        "description": "3 paragraphs: opening, one body, closing.",
        "rules": (
            "opening: 2-3 sentences — enthusiasm + company reference.\n"
            "body1:   3-4 sentences — strongest experience match + 1 metric + 1-2 relevant skills/projects.\n"
            'body2:   leave as empty string "".\n'
            "closing: 2-3 sentences — confident call-to-action."
        ),
    },
    4: {
        "description": "4 paragraphs: opening, body1, body2, closing (default — most complete).",
        "rules": (
            "opening: 2-3 sentences — enthusiasm + company reference.\n"
            "body1:   3-4 sentences — strongest experience match + 1 metric.\n"
            "body2:   3-4 sentences — skills/projects/tools that match the tech stack + 1 culture-fit sentence if company_description is provided.\n"
            "closing: 2-3 sentences — confident call-to-action."
        ),
    },
}


def _detect_paragraph_count(raw_specs: str | None) -> int:
    """
    Parse user specifications for an explicit paragraph preference.
    Looks for: '2 paragraph', '3 paragraph', 'two para', 'short', 'concise', etc.
    Returns 2, 3, or 4 (default).
    """
    if not raw_specs:
        return 4
    text = raw_specs.lower()

    # Explicit number words
    if any(k in text for k in ("two paragraph", "2 paragraph", "2-paragraph")):
        return 2
    if any(k in text for k in ("three paragraph", "3 paragraph", "3-paragraph")):
        return 3
    if any(k in text for k in ("four paragraph", "4 paragraph", "4-paragraph")):
        return 4

    # Intent signals
    if any(
        k in text
        for k in ("very short", "very brief", "super short", "2 para", "two para")
    ):
        return 2
    if any(k in text for k in ("short", "brief", "concise", "3 para", "three para")):
        return 3

    return 4


def _build_user_spec_block(raw: str | None, para_count: int) -> str:
    """
    Build the user-preferences block injected into the prompt.
    Paragraph-count instructions are always injected here (not in the rules above)
    so the model sees them as a firm instruction right before the schema.
    """
    cleaned = _sanitize_user_specifications(raw)

    lines = []

    # Always tell the model the paragraph count decision
    lines.append("=== PARAGRAPH COUNT (FIRM INSTRUCTION) ===")
    lines.append(
        f"Write EXACTLY {para_count} body paragraph(s) as described in the PARAGRAPH GUIDE above."
    )
    if para_count < 4:
        lines.append(
            'Any paragraph slot not needed MUST be returned as an empty string "" in the JSON.'
        )

    if cleaned:
        lines.append("")
        lines.append("=== CANDIDATE PREFERENCES (apply where relevant) ===")
        lines.append(
            "The candidate has provided the following notes. Apply ONLY content-related "
            "preferences (tone, emphasis, specific experience/project to highlight)."
        )
        lines.append("IGNORE any layout, colour, or font instructions.")
        lines.append("")
        lines.append(cleaned)
        lines.append("")
        lines.append("Rules for applying preferences:")
        lines.append(
            "- Mention a specific project/achievement → weave into body1 or body2 naturally."
        )
        lines.append(
            "- Specific tone (formal/conversational) → apply across all paragraphs."
        )
        lines.append(
            "- Highlight a specific skill → mention once in body1 or body2 where truthful."
        )
        lines.append(
            "- Do NOT fabricate experience, companies, or metrics not in the user data."
        )

    return "\n".join(lines)


def _build_sections_string(
    profile,
    email,
    experiences,
    projects,
    academics,
    skills,
    tools,
    achievements,
    publications,
    jd,
) -> str:
    parts = []

    profile_links = profile.get("links") or {}
    phone = profile.get("phone", "")
    linkedin = None

    if isinstance(profile_links, dict):
        phone = phone or profile_links.get("phone", "")
        linkedin = profile_links.get("linkedin")

    parts.append(
        f"CANDIDATE:\n"
        f"Name: {profile.get('full_name', '')}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Location: {profile.get('location', '')}\n"
        f"LinkedIn: {linkedin or 'not provided'}\n"
        f"Headline: {profile.get('headline', '')}\n"
        f"Summary: {profile.get('summary', 'not provided')}"
    )

    company_name = jd.get("company_name") or jd.get("company", "The Company")
    company_information = jd.get("company_information") or ""
    company_website_url = jd.get("company_website_url") or ""

    parts.append(
        f"TARGET JOB:\n"
        f"Role: {jd.get('role_name', '')}\n"
        f"Company: {company_name}\n"
        f"Company Description: {company_information or 'not provided'}\n"
        f"Company Website: {company_website_url or 'not provided'}\n"
        f"Tech Stack Required: {', '.join((jd.get('tech_stack') or [])[:12])}\n"
        f"Required Skills: {', '.join((jd.get('required_skills') or [])[:10])}\n"
        f"Job Description Summary: {jd.get('description', '') or jd.get('raw_text', '')}"
    )

    skill_names = [s.get("name", "") for s in skills if s.get("name")]
    tool_names = [t.get("name", "") for t in tools if t.get("name")]
    if skill_names or tool_names:
        parts.append(
            f"SKILLS:\nSkills: {', '.join(skill_names)}\nTools: {', '.join(tool_names)}"
        )

    if experiences:
        exp_lines = []
        for e in experiences:
            start_str = _fmt_date(e.get("start_month"), e.get("start_year"))
            end_str = _fmt_date(
                e.get("end_month"), e.get("end_year"), fallback="Present"
            )
            tech = ", ".join((e.get("techStack") or [])[:6])
            exp_lines.append(
                f"- Role: {e.get('role')}\n"
                f"  Company: {e.get('company_name')}\n"
                f"  Employment Type: {e.get('employment_type', '')}\n"
                f"  Start: {start_str} | End: {end_str}\n"
                f"  Tech: {tech}\n"
                f"  Description: {e.get('description', '')}"
            )
        parts.append("EXPERIENCE:\n" + "\n\n".join(exp_lines))

    if projects:
        proj_lines = []
        for p in projects[:2]:
            proj_lines.append(
                f"- Title: {p.get('title')}\n"
                f"  Tech: {', '.join((p.get('techStack') or [])[:5])}\n"
                f"  Description: {p.get('description', '')}"
            )
        parts.append(
            f"PROJECTS ({len(projects[:2])} provided — use only these):\n"
            + "\n\n".join(proj_lines)
        )

    if achievements:
        ach_lines = [
            f"- {a.get('title')} ({a.get('achievement_type', '')} {a.get('end_year', '')})"
            for a in achievements
        ]
        parts.append("ACHIEVEMENTS:\n" + "\n".join(ach_lines))

    if publications:
        pub_lines = [
            f"- {p.get('title')} | {p.get('publisher', '')} ({p.get('publication_date', '')})"
            for p in publications
        ]
        parts.append("PUBLICATIONS:\n" + "\n".join(pub_lines))

    if academics:
        edu_lines = []
        for a in academics:
            start_str = _fmt_date(a.get("start_month"), a.get("start_year"), "")
            end_str = _fmt_date(a.get("end_month"), a.get("end_year"), "Present")
            period = f"{start_str} – {end_str}".strip(" –")
            edu_lines.append(
                f"- Degree: {a.get('degree_name')} | Institution: {a.get('college_name')} | {period}"
            )
        parts.append("EDUCATION:\n" + "\n".join(edu_lines))

    return "\n\n".join(parts)


def _build_cover_letter_prompt(
    user_data: dict,
    user_specifications: str | None = None,
) -> str:
    profile = user_data.get("profile", {})
    experiences = user_data.get("experiences", [])
    projects = user_data.get("projects", [])
    academics = user_data.get("academics", [])
    skills = user_data.get("skills", [])
    tools = user_data.get("tools", [])
    publications = user_data.get("publications", [])
    achievements = user_data.get("achievements", [])
    jd = user_data.get("job_description", {})
    email = user_data.get("user", {}).get("email", "")

    company_name = jd.get("company_name") or jd.get("company", "the company")
    role_name = jd.get("role_name", "the role")
    today = datetime.now().strftime("%B %Y")

    # Detect desired paragraph count from user specs BEFORE sanitising
    para_count = _detect_paragraph_count(user_specifications)
    para_cfg = _PARA_CONFIGS[para_count]

    sections_data = _build_sections_string(
        profile,
        email,
        experiences,
        projects,
        academics,
        skills,
        tools,
        achievements,
        publications,
        jd,
    )
    user_spec_block = _build_user_spec_block(user_specifications, para_count)

    prompt = f"""You are an expert cover letter writer. Write a compelling, personalised cover letter.

CRITICAL: Output ONLY valid JSON matching the schema below. No markdown, no explanation, no extra keys.

=== TARGET ===
Role: {role_name}
Company: {company_name}
Today's Date: {today}

=== GENERAL WRITING RULES ===
1. ONE page only — do not exceed the paragraph count specified below.
2. Professional but warm tone. First-person. Not robotic.
3. Opening: genuine enthusiasm for THIS specific role + company. Reference company name. DO NOT start with "I am writing to".
4. Body paragraphs: connect candidate's REAL experience/skills to the job requirements. Include at least one specific metric if available.
5. Closing: confident call-to-action. Express eagerness to discuss.
6. NEVER fabricate experience, companies, or metrics not present in the user data.
7. Use the candidate's actual name, email, phone, and LinkedIn in the candidate object.
8. sign_off: use "Sincerely" unless user preferences say otherwise.

=== PARAGRAPH GUIDE — {para_cfg['description']} ===
{para_cfg['rules']}

{user_spec_block}

=== OUTPUT JSON SCHEMA ===
Return ONLY this JSON — no wrapping text, no markdown fences:

{{
  "candidate": {{
    "name": "string",
    "email": "string",
    "phone": "string or empty string",
    "location": "string or empty string",
    "linkedin": "string or null"
  }},
  "company": {{
    "name": "{company_name}",
    "role": "{role_name}"
  }},
  "date": "{today}",
  "paragraphs": {{
    "opening": "string",
    "body1":   "string  (empty string \"\" if not needed)",
    "body2":   "string  (empty string \"\" if not needed)",
    "closing": "string"
  }},
  "sign_off": "Sincerely"
}}

=== RAW USER DATA ===
{sections_data}

Return ONLY the JSON. No explanation. No markdown fences.
"""
    return prompt
