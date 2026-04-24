"""
Helper module to generate the resume generation prompt for AI.
Handles intelligent section ordering and formatting instructions.
"""


def build_resume_prompt(user_data: dict) -> str:
    """
    Build a strict prompt for generating a professional one-page resume.

    Args:
        user_data: Dictionary containing user profile, experiences, projects, etc.
                   (output from filter_jd)

    Returns:
        A detailed prompt string for the AI to generate resume text
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

    # Build sections in order (user controls section placement via priority)
    sections = []

    # 1. Header with contact info
    sections.append(
        f"""HEADER SECTION:
Name: {profile.get('full_name', 'Name')}
Headline: {profile.get('headline', '')}
Email: {user_data.get('user', {}).get('email', '')}
Links: {profile.get('links', 'N/A')}"""
    )

    # 2. Professional Summary (if available)
    if profile.get("summary"):
        sections.append(
            f"""PROFESSIONAL SUMMARY:
{profile.get('summary')}"""
        )

    # 3. Skills and Tools (all of them)
    if skills or tools:
        sections.append(
            f"""SKILLS & TECHNOLOGIES:
Skills: {', '.join([s.get('name', '') for s in skills])}
Tools: {', '.join([t.get('name', '') for t in tools])}"""
        )

    # 4. Relevant Experiences (all filtered experiences, already prioritized)
    if experiences:
        sections.append(
            f"""PROFESSIONAL EXPERIENCE:
{format_experiences(experiences)}"""
        )

    # 5. Projects (all filtered projects, already prioritized, 1-3 bullets each)
    if projects:
        sections.append(
            f"""PROJECTS:
{format_projects(projects)}"""
        )

    # 6. Achievements (all filtered achievements, already prioritized)
    if achievements:
        sections.append(
            f"""ACHIEVEMENTS & CERTIFICATIONS:
{format_achievements(achievements)}"""
        )

    # 7. Publications (if any)
    if publications:
        sections.append(
            f"""PUBLICATIONS:
{format_publications(publications)}"""
        )

    # 8. Education (user controls placement via priority in database)
    if academics:
        sections.append(
            f"""EDUCATION:
{format_education(academics)}"""
        )

    sections_str = "\n\n".join(sections)

    prompt = f"""You are a professional resume writer.

Your task is to generate a clean, ATS-friendly, ONE-PAGE resume in plain text format that will be directly used for PDF rendering.

TARGET JOB:
Role: {jd.get('role_name', 'Position')}
Company: {jd.get('company', 'Company')}
Key Skills: {', '.join(jd.get('tech_stack', [])[:8])}
Required Skills: {', '.join(jd.get('required_skills', [])[:8])}

====================
MANDATORY DATA USAGE
====================
- Use ALL relevant user data (experience, projects, education, achievements, publications)
- Do NOT ignore any section unless space constraints require trimming
- Prioritize content relevant to the job description

====================
DYNAMIC SECTION RULES
====================
- Include EDUCATION if provided
- Include PUBLICATIONS if:
  - job description contains AI/ML/Deep Learning/Data Science
  - OR user has publications
- Include PROJECTS if user has less than 2 years experience
- Include PROFESSIONAL SUMMARY only if:
  - user has < 3 years experience
  - OR additional context is needed
- Skip summary if experience is strong

====================
CONTENT ENHANCEMENT
====================
- Expand short inputs (1–2 lines) into strong, professional bullet points
- Add measurable impact where possible (%, scale, performance)
- Keep content realistic (DO NOT hallucinate)
- Use concise, high-impact language

====================
SKILLS FORMAT
====================
Group skills into categories:
Languages:
Frameworks & Libraries:
Backend & APIs:
Databases & ORMs:
DevOps & Tools:

====================
BULLET RULES
====================
- Start with strong action verbs (Built, Engineered, Designed, Optimized)
- Each bullet must show impact or outcome
- One line per bullet
- Avoid generic phrases like "worked on"

====================
HEADER FORMAT
====================
Name
Role / Title
Email | GitHub | Portfolio | LinkedIn

(No emojis, no markdown symbols)

====================
PDF RENDERING RULES (CRITICAL)
====================
- Output must be clean plain text (NO markdown, NO symbols like **, [], etc.)
- Use consistent spacing between sections (one blank line only)
- Do NOT use tabs or irregular spacing
- Do NOT include emojis or special characters
- Keep line lengths reasonable (avoid very long lines)
- Ensure formatting is consistent so it can be directly converted to PDF
- Section headers must be in UPPERCASE

====================
SECTION ORDER
====================
Header
Professional Summary (if needed)
Skills & Technologies
Professional Experience
Projects
Achievements & Certifications
Publications (if applicable)
Education

====================
CONTENT FOCUS
====================
- Match resume content with job description keywords
- Highlight relevant technologies from tech_stack and required_skills
- Remove generic or filler content
- Keep everything concise to fit ONE PAGE

====================
OUTPUT RULES
====================
- Start with: "[Full Name] - Resume"
- Output ONLY the final resume text
- Do NOT include explanations

====================
USER DATA
====================
{sections_str}

GENERATE THE FINAL RESUME NOW.
"""

    return prompt


def format_experiences(experiences: list) -> str:
    """Format professional experiences for the prompt."""
    if not experiences:
        return ""

    formatted = []
    for exp in experiences:
        company = exp.get("company_name", "Company")
        role = exp.get("role", "Role")
        dates = f"{exp.get('start_year', '')}" + (
            f"-{exp.get('end_year', '')}" if exp.get("end_year") else "-Present"
        )
        location = exp.get("location_details", "")
        description = exp.get("description", "")
        tech_stack = exp.get("techStack", [])

        tech_str = f" | Tech: {', '.join(tech_stack[:5])}" if tech_stack else ""
        location_str = f" | {location}" if location else ""

        formatted.append(
            f"{role} at {company} ({dates}){location_str}{tech_str}\n{description}"
        )

    return "\n\n".join(formatted)


def format_projects(projects: list) -> str:
    """Format projects with 1-2 bullet points each."""
    if not projects:
        return ""

    formatted = []
    for proj in projects:  # Send all filtered projects
        title = proj.get("title", "Project")
        description = proj.get("description", "")
        tech_stack = proj.get("techStack", [])
        links = proj.get("links", {})

        tech_str = f" | Tech: {', '.join(tech_stack[:4])}" if tech_stack else ""

        formatted.append(f"{title}{tech_str}\n• {description}")

    return "\n\n".join(formatted)


def format_achievements(achievements: list) -> str:
    """Format achievements."""
    if not achievements:
        return ""

    formatted = []
    for ach in achievements:  # Send all filtered achievements
        title = ach.get("title", "Achievement")
        achievement_type = ach.get("achievement_type", "")
        year = ach.get("end_year", "")

        type_str = f" - {achievement_type}" if achievement_type else ""
        year_str = f" ({year})" if year else ""

        formatted.append(f"• {title}{type_str}{year_str}")

    return "\n".join(formatted)


def format_education(academics: list) -> str:
    """Format education."""
    if not academics:
        return ""

    formatted = []
    for acad in academics:
        degree = acad.get("degree_name", "Degree")
        college = acad.get("college_name", "College")
        year = acad.get("end_year", "")

        year_str = f" ({year})" if year else ""
        formatted.append(f"{degree} from {college}{year_str}")

    return "\n".join(formatted)


def format_publications(publications: list) -> str:
    """Format publications."""
    if not publications:
        return ""

    formatted = []
    for pub in publications:  # Send all filtered publications
        title = pub.get("title", "Publication")
        publisher = pub.get("publisher", "")
        year = pub.get("publication_date", "")

        publisher_str = f" | {publisher}" if publisher else ""
        year_str = f" ({year})" if year else ""

        formatted.append(f"• {title}{publisher_str}{year_str}")

    return "\n".join(formatted)
