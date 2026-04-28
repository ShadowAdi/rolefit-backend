"""
Resume generation prompt builder.
Produces structured JSON consumed directly by build_pdf.py.
"""


def _label_links(links) -> list[str]:
    if not links:
        return []
    label_map = {
        "github": "GitHub",
        "live": "Live",
        "vercel": "Live",
        "demo": "Demo",
        "url": "Link",
        "website": "Website",
        "paper": "Paper",
        "arxiv": "arXiv",
    }
    labelled = []
    if isinstance(links, dict):
        for key, url in links.items():
            if url:
                label = label_map.get(key.lower(), key.capitalize())
                labelled.append(f"{label}::{url}")
    elif isinstance(links, list):
        default_labels = ["GitHub", "Live", "Demo", "Link"]
        for i, url in enumerate(links):
            if url:
                label = default_labels[i] if i < len(default_labels) else "Link"
                labelled.append(f"{label}::{url}")
    return labelled


def _estimate_years(experiences: list) -> float:
    total = 0
    for exp in experiences:
        start = int(exp.get("start_year", 0) or 0)
        end = int(exp.get("end_year", 0) or 0)
        if start and end:
            total += max(0, end - start)
    return total


def _is_ml_role(jd: dict) -> bool:
    ml_keywords = {
        "ml",
        "machine learning",
        "deep learning",
        "ai",
        "data science",
        "nlp",
        "llm",
    }
    text = (jd.get("role_name", "") + " " + " ".join(jd.get("tech_stack", []))).lower()
    return any(kw in text for kw in ml_keywords)


_BLOCKED_SPEC_KEYWORDS = [
    "color",
    "colour",
    "theme",
    "font",
    "layout",
    "margin",
    "padding",
    "template",
    "border",
    "background",
    "page size",
    "column",
    "sidebar",
    "header style",
    "footer",
    "section order",
    "reorder sections",
    "move section",
    "remove section",
    "add section",
]


def _sanitize_user_specifications(raw: str | None) -> str | None:
    """
    Strip out any layout/color/structural requests from user_specifications.
    Returns cleaned text, or None if nothing useful remains.
    """
    if not raw or not raw.strip():
        return None

    lines = raw.strip().splitlines()
    allowed_lines = []

    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in _BLOCKED_SPEC_KEYWORDS):
            continue
        allowed_lines.append(line.strip())

    cleaned = "\n".join(l for l in allowed_lines if l)
    return cleaned if cleaned else None


def _build_user_spec_block(raw: str | None) -> str:
    """
    Build the prompt section for user specifications.
    Returns an empty string if there are no valid specs.
    """
    cleaned = _sanitize_user_specifications(raw)
    if not cleaned:
        return ""

    return f"""
=== USER PREFERENCES (Optional — apply where relevant) ===
The candidate has provided the following preferences for this resume.
Apply ONLY what is content-related (emphasis, ordering within sections, skill/project/tech highlighting).
IGNORE any layout, color, font, or structural instructions — those are fixed.

{cleaned}

Rules for applying preferences:
- If the user asks to emphasize a specific project → place it first in the projects array and expand its bullets slightly within the word limit.
- If the user asks to highlight specific skills or tools → list them first within their skill category.
- If the user asks to highlight specific tech stack items → naturally mention them in relevant bullets where truthful.
- If the user asks to give importance to a degree or coursework → write a richer "description" field for that education entry.
- If the user asks to prioritize a specific work experience → list it first and use the maximum allowed bullets for it.
- Do NOT invent or fabricate any content that the user has not provided in their data.
- Do NOT exceed the one-page content limits defined above.
"""


def build_resume_prompt(user_data: dict, user_specifications: str | None = None) -> str:
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

    years_experience = _estimate_years(experiences)
    has_projects = bool(projects)
    has_achievements = bool(achievements)
    include_publications = bool(publications) or _is_ml_role(jd)

    is_senior = years_experience >= 3
    include_projects = has_projects and not is_senior
    include_summary = not is_senior

    sections_data = _build_sections_string(
        profile,
        email,
        experiences,
        projects,
        academics,
        skills,
        tools,
        publications,
        achievements,
        include_projects,
        include_publications,
        has_achievements,
    )

    # Dynamic content limits based on experience
    exp_bullet_limit = 3 if not is_senior else 4
    proj_section = (
        "- Projects: MAX 2 projects (ONLY from user-provided projects). MAX 2 bullets each. Each bullet MIN 10 words MAX 30 words."
        if include_projects
        else "- Projects: Return empty array [] — candidate has sufficient experience."
    )
    summary_section = (
        "- Summary: EXACTLY 2-3 sentences. First: years + core stack. Second: value for this role."
        if include_summary
        else '- Summary: Return empty string "" — not needed for senior profiles.'
    )
    achievements_section = (
        f"- Achievements: Use ONLY the {len(achievements)} achievement(s) provided by user. Do NOT invent any."
        if has_achievements
        else "- Achievements: Return empty array [] — user has not added any achievements."
    )

    # Build optional user spec block (empty string if not provided / all blocked)
    user_spec_block = _build_user_spec_block(user_specifications)

    prompt = f"""You are an expert resume writer and ATS optimization specialist.

CRITICAL: Output MUST fit ONE PAGE. Follow content limits exactly.
Output MUST be valid JSON. No markdown, no prose, no extra keys.

=== TARGET JOB ===
Role: {jd.get('role_name', '')}
Company: {jd.get('company', '')}
Tech Stack: {', '.join(jd.get('tech_stack', [])[:10])}
Required Skills: {', '.join(jd.get('required_skills', [])[:10])}

=== ONE-PAGE CONTENT LIMITS (HARD) ===
{summary_section}
- Experience: MAX {exp_bullet_limit} bullets per role. Each bullet MIN 10 words MAX 30 words. One line only.
{proj_section}
{achievements_section}
- Skills: List items only — no explanations.
- Education: Always include a 1-sentence description of what the candidate studied, even if not provided. Infer from degree name (e.g. BCA → computer science fundamentals, data structures, web development; BA Arts → literature, communication, humanities).

=== WRITING RULES ===
1. Start bullets with action verbs: Built, Engineered, Reduced, Shipped, Optimized, Automated, Led.
2. Include ONE metric per bullet (%, users, ms). If missing, add a realistic one.
3. No sub-bullets. No filler phrases.
4. Match keywords from tech_stack and required_skills naturally.

=== SKILLS RULES ===
- Include ALL skills and tools provided — do NOT drop any.
- Categories: Languages | Frameworks & Libraries | Databases & ORMs | DevOps & Cloud | Other Tools
- Skip role-name entries: "frontend", "backend", "full stack", "ui designer", "infra", "system design".
- Normalize: nodejs→Node.js, nextjs→Next.js, netjs→NestJS, golang→Go, postgres→PostgreSQL, cpp→C++, tailwind css→Tailwind CSS.

=== EXPERIENCE RULES ===
- Dates are pre-formatted "Mon YYYY" — use exactly as given.
- "emp_type" field: employment type only — e.g. "Internship", "Full-time", "Contract", "Part-time". Nothing else.
- "company" field: just the company name. No location, no remote/onsite info.
- MAX {exp_bullet_limit} bullets per role, each MIN 10 words and MAX 30 words.

=== PROJECT RULES ===
- ONLY include projects the user explicitly provided. Never invent or infer projects.
- If user provided 0 projects, return projects as empty array [].
- Links are "Label::URL" strings — copy exactly, do not modify.
- MAX 2 bullets per project, each MIN 10 words and MAX 30 words.

=== ACHIEVEMENTS RULES ===
- ONLY use achievements explicitly provided by the user (hackathons won, competitions, awards, certifications they listed).
- NEVER generate achievements from experience bullets or project descriptions.
- If user provided 0 achievements, return empty array [].

=== EDUCATION RULES ===
- Expand degree abbreviations: BCA → Bachelor of Computer Applications (BCA), MBA → Master of Business Administration (MBA).
- "description" field: Write 1 sentence about what the degree covers. Infer from degree name if user didn't provide details.
  Examples: BCA → "Studied computer science fundamentals, data structures, algorithms, and web development."
            BA English → "Studied English literature, communication, writing, and humanities."
            B.Tech CSE → "Studied software engineering, algorithms, operating systems, and computer networks."
{user_spec_block}
=== OUTPUT JSON SCHEMA ===
Return ONLY this JSON — no wrapping text, no markdown fences:

{{
  "header": {{"name": "string", "title": "string", "email": "string", "phone": "string", "location": "string", "links": ["string"]}},
  "summary": "string",
  "skills": [{{"category": "string", "items": ["string"]}}],
    "experience": [{{"role": "string", "company": "string", "emp_type": "string", "start": "string", "end": "string", "bullets": ["string"]}}],
  "projects": [{{"title": "string", "tech": "string", "bullets": ["string"], "links": ["string"]}}],
  "achievements": ["string"],
  "publications": [{{"title": "string", "publisher": "string", "year": "string"}}],
  "education": [{{"degree": "string", "institution": "string", "location": "string", "year": "string", "description": "string"}}]
}}

=== RAW USER DATA ===
{sections_data}

Return ONLY the JSON. No explanation. No markdown fences.
"""
    return prompt


def _build_sections_string(
    profile,
    email,
    experiences,
    projects,
    academics,
    skills,
    tools,
    publications,
    achievements,
    include_projects,
    include_publications,
    has_achievements,
) -> str:
    parts = []

    profile_links = profile.get("links") or {}
    phone = profile.get("phone", "")
    header_links = []
    if isinstance(profile_links, dict):
        phone = phone or profile_links.get("phone", "")
        for key, val in profile_links.items():
            if key.lower() != "phone" and val:
                header_links.append(val)
    elif isinstance(profile_links, list):
        header_links = [l for l in profile_links if l]

    parts.append(
        f"HEADER:\n"
        f"Name: {profile.get('full_name', '')}\n"
        f"Title: {profile.get('headline', '')}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Location: {profile.get('location', '')}\n"
        f"Links: {', '.join(header_links)}"
    )

    existing = profile.get("summary", "")
    if existing:
        parts.append(
            f"EXISTING SUMMARY (condense to 2 sentences, tailor to role):\n{existing}"
        )
    else:
        parts.append(
            "SUMMARY: No existing summary. Write exactly 2 sentences from experience below."
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

    if include_projects and projects:
        proj_lines = []
        for p in projects[:2]:
            tech = ", ".join((p.get("techStack") or [])[:5])
            labelled = _label_links(p.get("links"))
            proj_lines.append(
                f"- Title: {p.get('title')}\n"
                f"  Tech: {tech}\n"
                f"  Description: {p.get('description', '')}\n"
                f"  Links: {', '.join(labelled)}"
            )
        titles = [p.get("title") for p in projects[:2]]
        parts.append(
            f"PROJECTS: User has exactly {len(projects[:2])} project(s). "
            f"Use ONLY these titles: {titles}. Do not add any others.\n\n"
            + "\n\n".join(proj_lines)
        )
    else:
        parts.append('PROJECTS: "projects": []')

    if has_achievements and achievements:
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

    if include_publications and publications:
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
