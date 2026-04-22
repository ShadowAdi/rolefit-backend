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

    # Determine if education should be at top or bottom
    # Rule: If not from top college, put at bottom
    education_at_bottom = False
    top_colleges = [
        "iit",
        "mit",
        "stanford",
        "harvard",
        "berkeley",
        "cmu",
        "oxford",
        "cambridge",
        "top tier",
        "ivy league",
    ]

    if academics:
        college_name = academics[0].get("college_name", "").lower()
        if not any(tier in college_name for tier in top_colleges):
            education_at_bottom = True

    # Build sections based on priority
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

    # 3. Skills and Tools (highly relevant to JD)
    if skills or tools:
        sections.append(
            f"""SKILLS & TECHNOLOGIES:
Skills: {', '.join([s.get('name', '') for s in skills[:8]])}
Tools: {', '.join([t.get('name', '') for t in tools[:5]])}"""
        )

    # 4. Relevant Experiences (top 3 from filter)
    if experiences:
        sections.append(
            f"""PROFESSIONAL EXPERIENCE:
{format_experiences(experiences)}"""
        )

    # 5. Projects (top 3 from filter, 1-3 bullets each)
    if projects:
        sections.append(
            f"""PROJECTS:
{format_projects(projects)}"""
        )

    # 6. Achievements
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

    # 8. Education (top or bottom based on tier)
    if academics and not education_at_bottom:
        sections.append(
            f"""EDUCATION:
{format_education(academics)}"""
        )

    sections_str = "\n\n".join(sections)

    # Add education at bottom if low tier
    if academics and education_at_bottom:
        sections_str += f"\n\nEDUCATION:\n{format_education(academics)}"

    # Build the main prompt
    prompt = f"""You are a professional resume writer. Generate a clean, ATS-friendly, ONE-PAGE resume in plain text format.

TARGET JOB:
Role: {jd.get('role_name', 'Position')}
Company: {jd.get('company', 'Company')}
Key Skills: {', '.join(jd.get('tech_stack', [])[:8])}
Required Skills: {', '.join(jd.get('required_skills', [])[:8])}

USER DATA TO USE:
{sections_str}

STRICT FORMATTING RULES:
1. **ONE PAGE MAXIMUM** - Fit everything on a single page
2. **Bullet Points**: Use 1-3 bullets per position/project (max 2 for projects)
3. **No Lorem Ipsum** - Use actual data provided
4. **Action Verbs**: Start each bullet with strong action verbs (Developed, Built, Led, Designed, etc.)
5. **Quantify Achievements**: Include metrics where possible (e.g., "Improved performance by 40%")
6. **ATS Compatible**: 
   - No tables, images, or special formatting
   - Use standard section headers
   - Clean plain text only
7. **Section Order** (if space allows):
   - Header (Name, Headline, Email, Links)
   - Professional Summary (2-3 lines max, optional if space tight)
   - Skills & Technologies
   - Professional Experience (top 3 only)
   - Projects (top 3 only, 1-2 bullets each)
   - Achievements & Certifications (top 3 only)
   - Publications (if space available)
   - Education (at bottom if from tier 3/non-top college)

8. **Content Focus**:
   - Prioritize experiences and projects matching the JD keywords
   - Highlight technical skills from tech_stack and required_skills
   - Remove generic descriptions - be specific
   - Use concise language to fit one page

9. **Resume Name Format**:
   Start with: "[Full Name] - Resume"

GENERATE THE COMPLETE RESUME TEXT NOW. Output ONLY the resume text, no explanations."""

    return prompt


def format_experiences(experiences: list) -> str:
    """Format professional experiences for the prompt."""
    if not experiences:
        return ""

    formatted = []
    for exp in experiences[:3]:  # Top 3 experiences
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
    for proj in projects[:3]:  # Top 3 projects
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
    for ach in achievements[:5]:  # Top 5 achievements
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
    for pub in publications[:3]:  # Top 3 publications
        title = pub.get("title", "Publication")
        publisher = pub.get("publisher", "")
        year = pub.get("publication_date", "")

        publisher_str = f" | {publisher}" if publisher else ""
        year_str = f" ({year})" if year else ""

        formatted.append(f"• {title}{publisher_str}{year_str}")

    return "\n".join(formatted)
