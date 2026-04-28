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
    publications: list,
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

    skill_names = [s.get("name", "") for s in skills if s.get("name")]
    tool_names = [t.get("name", "") for t in tools if t.get("name")]
    if skill_names or tool_names:
        parts.append(
            f"SKILLS (include ALL, do not drop any):\n"
            f"Skills: {', '.join(skill_names)}\n"
            f"Tools: {', '.join(tool_names)}"
        )

    if experiences:
        exp_lines = []
        for e in experiences:
            start_str = _fmt_date(e.get("start_month"), e.get("start_year"))
            end_str = _fmt_date(
                e.get("end_month"), e.get("end_year"), fallback="Present"
            )
            tech = ", ".join((e.get("techStack") or [])[:6])
            emp_type = e.get("employment_type", "")

            exp_lines.append(
                f"- Role: {e.get('role')}\n"
                f"  Company: {e.get('company_name')}\n"
                f"  Employment Type: {emp_type}\n"
                f"  Start: {start_str}\n"
                f"  End: {end_str}\n"
                f"  Tech: {tech}\n"
                f"  Description: {e.get('description', '')}"
            )
        parts.append("EXPERIENCE:\n" + "\n\n".join(exp_lines))

    if projects:
        proj_lines = []
        for p in projects[:2]:
            tech = ", ".join((p.get("techStack") or [])[:5])
            proj_lines.append(
                f"- Title: {p.get('title')}\n"
                f"  Tech: {tech}\n"
                f"  Description: {p.get('description', '')}\n"
            )
        titles = [p.get("title") for p in projects[:2]]
        parts.append(
            f"PROJECTS: User has exactly {len(projects[:2])} project(s). "
            f"Use ONLY these titles: {titles}. Do not add any others.\n\n"
            + "\n\n".join(proj_lines)
        )
    else:
        parts.append('PROJECTS: "projects": []')

    if achievements:
        ach_lines = [
            f"- {a.get('title')} ({a.get('achievement_type', '')} {a.get('end_year', '')})"
            for a in achievements
        ]
        parts.append(
            f"ACHIEVEMENTS: User has exactly {len(achievements)} achievement(s). "
            f"Use only these:\n" + "\n".join(ach_lines)
        )
    else:
        parts.append('ACHIEVEMENTS: "achievements": []')

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
                f"- Degree: {a.get('degree_name')}\n"
                f"  Institution: {a.get('college_name')}\n"
                f"  Period: {period}\n"
                f"  Description: {a.get('description') or 'Not provided — infer from degree name.'}"
            )
        parts.append("EDUCATION:\n" + "\n\n".join(edu_lines))

    return "\n\n".join(parts)


def _build_cover_letter_prompt(
    user_data: dict, user_specifications: str | None = None
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

    sections_data = _build_sections_string(
        profile=profile,
        email=email,
        experiences=experiences,
        projects=projects,
        academics=academics,
        achievements=achievements,
        skills=skills,
        tools=tools,
        publications=publications,
        jd=jd,
    )

    user_spec_block = _build_user_spec_block(user_specifications)

    prompt = f"""You are an expert cover letter writer. Write a compelling, personalised, one-page cover letter.
 
CRITICAL: Output ONLY valid JSON matching the schema below. No markdown, no explanation, no extra keys.
 
=== TARGET ===
Role: {role_name}
Company: {company_name}
Today's Date: {today}
 
=== WRITING RULES ===
1. ONE page only — four short paragraphs total (opening, body1, body2, closing).
2. Each paragraph: 2-4 sentences MAX. No padding, no fluff.
3. Opening: Express genuine enthusiasm for the specific role + company. Reference company name. DO NOT start with "I am writing to".
4. Body1: Connect the candidate's STRONGEST and MOST RELEVANT experience to the job requirements. Include one specific metric or achievement if available.
5. Body2: Highlight 2-3 skills/projects/tools that directly match the job's tech stack or requirements. If company_description is provided, mention 1 thing about why the company mission resonates.
6. Closing: Confident call-to-action. Express eagerness to discuss further.
7. Tone: Professional but warm. Not robotic. First-person.
8. NEVER fabricate experience, companies, or metrics not present in the user data.
9. Use the candidate's actual name, email, phone, and LinkedIn in the candidate object.
10. sign_off: use "Sincerely" unless user_specifications say otherwise.
 
=== PARAGRAPH LENGTH GUIDE ===
- opening: 2-3 sentences
- body1:   3-4 sentences (strongest experience match + metric)
- body2:   3-4 sentences (skills / projects / culture fit)  
- closing: 2-3 sentences (call to action)
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
    "body1":   "string",
    "body2":   "string",
    "closing": "string"
  }},
  "sign_off": "Sincerely"
}}
 
=== RAW USER DATA ===
{sections_data}
 
Return ONLY the JSON. No explanation. No markdown fences.
"""
    return prompt
