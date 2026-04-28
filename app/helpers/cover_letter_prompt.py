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


def _build_sections_string(
    profile: dict,
    email: str,
    experiences: list,
    projects: list,
    academics: list,
    skills: list,
    tools: list,
    achievements: list,
    jd: dict,
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

    if experiences:
        exp_lines = []
        for e in experiences[:4]:
            start_str = _fmt_date(e.get("start_month"), e.get("start_year"))
            end_str = _fmt_date(
                e.get("end_month"), e.get("end_year"), fallback="Present"
            )
            tech = ", ".join((e.get("techStack") or [])[:6])
            exp_lines.append(
                f"- Role: {e.get('role')} at {e.get('company_name')}\n"
                f"  Period: {start_str} – {end_str}\n"
                f"  Tech: {tech}\n"
                f"  Description: {e.get('description', '')}"
            )
        parts.append(
            "EXPERIENCE (use most relevant to role):\n" + "\n\n".join(exp_lines)
        )
    else:
        parts.append("EXPERIENCE: None provided.")

    skill_names = [s.get("name", "") for s in skills if s.get("name")]
    tool_names = [t.get("name", "") for t in tools if t.get("name")]
    if skill_names or tool_names:
        parts.append(
            f"SKILLS & TOOLS:\n"
            f"Skills: {', '.join(skill_names)}\n"
            f"Tools: {', '.join(tool_names)}"
        )

    if projects:
        proj_lines = []
        for p in projects[:3]:
            tech = ", ".join((p.get("techStack") or [])[:5])
            proj_lines.append(
                f"- {p.get('title')}: {p.get('description', '')} (Tech: {tech})"
            )
        parts.append("PROJECTS:\n" + "\n".join(proj_lines))

    if achievements:
        ach_lines = [
            f"- {a.get('title')} ({a.get('achievement_type', '')} {a.get('end_year', '')})"
            for a in achievements
        ]
        parts.append("ACHIEVEMENTS:\n" + "\n".join(ach_lines))

    if academics:
        edu_lines = []
        for a in academics:
            end_str = _fmt_date(a.get("end_month"), a.get("end_year"), "Present")
            edu_lines.append(
                f"- {a.get('degree_name')} from {a.get('college_name')} ({end_str})"
            )
        parts.append("EDUCATION:\n" + "\n".join(edu_lines))

    return "\n\n".join(parts)
