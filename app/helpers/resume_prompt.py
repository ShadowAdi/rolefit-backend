"""
Resume generation prompt builder.
Produces a structured JSON schema instead of plain text,
so the PDF renderer can work with typed data instead of
trying to parse free-form text.
"""


def build_resume_prompt(user_data: dict) -> str:
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

    include_summary = years_experience < 3
    include_projects = years_experience < 2 or bool(projects)
    include_publications = bool(publications) or _is_ml_role(jd)

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
        include_summary,
        include_projects,
        include_publications,
    )

    prompt = f"""You are an expert resume writer and ATS optimization specialist.

Your task: transform the raw user data below into a polished, one-page resume.
Output MUST be valid JSON matching the exact schema shown. No markdown, no prose, no extra keys.

=== TARGET JOB ===
Role: {jd.get('role_name', '')}
Company: {jd.get('company', '')}
Tech Stack: {', '.join(jd.get('tech_stack', [])[:10])}
Required Skills: {', '.join(jd.get('required_skills', [])[:10])}

=== WRITING RULES ===
1. Bullet points: start with a strong past-tense action verb (Built, Engineered, Reduced, Shipped, Designed, Automated, Migrated, Optimized, Led, Implemented).
2. Every bullet must contain ONE measurable outcome or scale signal (%, users, ms, requests/sec, lines of code, team size). If raw data lacks a number, add a realistic one that fits the context — do NOT hallucinate company names or technologies.
3. Each bullet is ONE concise line. No sub-bullets.
4. Match keywords from tech_stack and required_skills into experience/project bullets naturally.
5. Remove filler phrases: "worked on", "responsible for", "helped with", "assisted in".
6. Skills section: group into exactly these categories (omit a category if empty):
   Languages | Frameworks & Libraries | Databases & ORMs | DevOps & Cloud | Other Tools

=== CONTENT SELECTION RULES ===
- Include summary: {include_summary} (only for < 3 years experience or career changers)
- Include projects: {include_projects}
- Include publications: {include_publications}
- Max experience bullets per role: 4
- Max project bullets: 2 per project, max 3 projects total
- If space is tight, trim oldest/least-relevant experience first

=== OUTPUT JSON SCHEMA ===
Return ONLY this JSON object, no wrapping text:

{{
  "header": {{
    "name": "string",
    "title": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "links": ["string"]
  }},
  "summary": "string or null",
  "skills": [
    {{"category": "string", "items": ["string"]}}
  ],
  "experience": [
    {{
      "role": "string",
      "company": "string",
      "location": "string",
      "start": "string",
      "end": "string",
      "bullets": ["string"]
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "tech": "string",
      "bullets": ["string"],
      "links": ["string"]
    }}
  ],
  "achievements": ["string"],
  "publications": [
    {{
      "title": "string",
      "publisher": "string",
      "year": "string"
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "location": "string",
      "year": "string"
    }}
  ]
}}

=== RAW USER DATA ===
{sections_data}

Return ONLY the JSON. No explanation. No markdown fences.
"""
    return prompt


# ── helpers ──────────────────────────────────────────────────────────────────


def _estimate_years(experiences: list) -> float:
    total = 0
    for exp in experiences:
        start = int(exp.get("start_year", 0) or 0)
        end = int(exp.get("end_year", 0) or 0)
        if start:
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

    text = jd.get("role_name", "") + " " + " ".join(jd.get("tech_stack", [])).lower()
    return any(kw in text for kw in ml_keywords)


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
    include_summary,
    include_projects,
    include_publications,
) -> str:
    parts = []

    parts.append(
        f"""HEADER:
Name: {profile.get('full_name', '')}
Title: {profile.get('headline', '')}
Email: {email}
Phone: {profile.get('phone', '')}
Location: {profile.get('location', '')}
Links: {profile.get('links', '')}"""
    )

    if include_summary and profile.get("summary"):
        parts.append(f"SUMMARY:\n{profile['summary']}")

    all_skills = [s.get("name", "") for s in skills] + [
        t.get("name", "") for t in tools
    ]
    if all_skills:
        parts.append(f"SKILLS (raw, group and clean these):\n{', '.join(all_skills)}")

    if experiences:
        exp_lines = []
        for e in experiences:
            end = e.get("end_year") or "Present"
            tech = ", ".join(e.get("techStack", [])[:6])
            exp_lines.append(
                f"- {e.get('role')} @ {e.get('company_name')} "
                f"({e.get('start_year')}–{end}) | {e.get('location_details', '')}\n"
                f"  Tech: {tech}\n"
                f"  Description: {e.get('description', '')}"
            )
        parts.append("EXPERIENCE:\n" + "\n\n".join(exp_lines))

    if include_projects and projects:
        proj_lines = []
        for p in projects[:4]:
            tech = ", ".join(p.get("techStack", [])[:5])
            proj_lines.append(
                f"- {p.get('title')} | Tech: {tech}\n"
                f"  {p.get('description', '')}\n"
                f"  Links: {p.get('links', '')}"
            )
        parts.append("PROJECTS:\n" + "\n\n".join(proj_lines))

    if achievements:
        ach_lines = [
            f"- {a.get('title')} ({a.get('achievement_type', '')} {a.get('end_year', '')})"
            for a in achievements
        ]
        parts.append("ACHIEVEMENTS:\n" + "\n".join(ach_lines))

    if include_publications and publications:
        pub_lines = [
            f"- {p.get('title')} | {p.get('publisher', '')} ({p.get('publication_date', '')})"
            for p in publications
        ]
        parts.append("PUBLICATIONS:\n" + "\n".join(pub_lines))

    if academics:
        edu_lines = [
            f"- {a.get('degree_name')} | {a.get('college_name')} ({a.get('end_year', '')})"
            for a in academics
        ]
        parts.append("EDUCATION:\n" + "\n".join(edu_lines))

    return "\n\n".join(parts)
