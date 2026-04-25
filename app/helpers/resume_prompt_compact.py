"""
Resume generation prompt builder.
Produces structured JSON consumed directly by build_pdf.py.
"""

MONTH_MAP = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def _fmt_date(month, year, fallback: str = "Present") -> str:
    """Convert month int + year int to 'Nov 2025' style string."""
    if year and month:
        return f"{MONTH_MAP.get(int(month), '')} {year}"
    if year:
        return str(year)
    return fallback


def _label_links(links) -> list[str]:
    """
    Convert raw link dict or list into labelled strings.
    e.g. {"github": "https://..."} -> ["GitHub::https://..."]
    The PDF renderer uses the label as display text and URL as href.
    """
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

    existing_summary = profile.get("summary", "")
    if existing_summary:
        parts.append(
            f"EXISTING SUMMARY (improve, expand to 3-4 sentences, tailor to target role):\n"
            f"{existing_summary}"
        )
    else:
        parts.append(
            "SUMMARY INSTRUCTION: No existing summary provided. "
            "Write a strong 3-4 sentence summary from scratch using the experience and projects below. "
            "Sell the candidate's potential and match the target role."
        )

    skill_names = [s.get("name", "") for s in skills if s.get("name")]
    tool_names = [t.get("name", "") for t in tools if t.get("name")]
    if skill_names or tool_names:
        parts.append(
            f"SKILLS (include ALL — do not omit any):\n"
            f"Skill entries: {', '.join(skill_names)}\n"
            f"Tool entries: {', '.join(tool_names)}"
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
            loc_type = e.get("location_type", "")
            loc_detail = e.get("location_details") or loc_type or ""

            exp_lines.append(
                f"- Role: {e.get('role')}\n"
                f"  Company: {e.get('company_name')}\n"
                f"  Location Type: {loc_detail}\n"
                f"  Employment Type: {emp_type}\n"
                f"  Start: {start_str}\n"
                f"  End: {end_str}\n"
                f"  Tech: {tech}\n"
                f"  Description: {e.get('description', '')}"
            )
        parts.append("EXPERIENCE:\n" + "\n\n".join(exp_lines))

    if include_projects and projects:
        proj_lines = []
        for p in projects[:4]:
            tech = ", ".join((p.get("techStack") or [])[:5])
            labelled = _label_links(p.get("links"))
            proj_lines.append(
                f"- Title: {p.get('title')}\n"
                f"  Tech: {tech}\n"
                f"  Description: {p.get('description', '')}\n"
                f"  Links: {', '.join(labelled)}"
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
        edu_lines = []
        for a in academics:
            start_str = _fmt_date(a.get("start_month"), a.get("start_year"), "")
            end_str = _fmt_date(a.get("end_month"), a.get("end_year"), "Present")
            period = f"{start_str} – {end_str}".strip(" –")
            edu_lines.append(
                f"- Degree: {a.get('degree_name')}\n"
                f"  Institution: {a.get('college_name')}\n"
                f"  Period: {period}\n"
                f"  Description: {a.get('description') or 'N/A'}"
            )
        parts.append("EDUCATION:\n" + "\n\n".join(edu_lines))

    return "\n\n".join(parts)


def build_resume_prompt_compact(user_data: dict) -> str:
    """
    Ultra-compact prompt for models with ~2000 token limits (e.g. Sarvam).
    Strips verbose rules, keeps only schema + data.
    """
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
    include_projects = years_experience < 2 or bool(projects)
    include_publications = bool(publications) or _is_ml_role(jd)

    # Build minimal data string
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
    )

    return f"""Output ONLY valid JSON. No markdown. No explanation. No <think>.

Job: {jd.get('role_name','')} at {jd.get('company','')}
Skills needed: {', '.join(jd.get('required_skills', [])[:6])}

Rules: bullets start with action verb + measurable outcome. 3-4 sentence summary always. Normalize skill names (nodejs→Node.js etc).

Schema:
{{"header":{{"name":"","title":"","email":"","phone":"","location":"","links":[]}},"summary":"","skills":[{{"category":"","items":[]}}],"experience":[{{"role":"","company":"","location":"","start":"","end":"","bullets":[]}}],"projects":[{{"title":"","tech":"","bullets":[],"links":[]}}],"achievements":[],"publications":[{{"title":"","publisher":"","year":""}}],"education":[{{"degree":"","institution":"","location":"","year":""}}]}}

Data:
{sections_data}

JSON:"""
