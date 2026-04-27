from sqlalchemy.orm import Session

from app.models.Profile import Profile
from app.models.Experience import Experience
from app.models.Academic import Academic
from app.models.Achievement import Achievement
from app.models.Project import Project
from app.models.Publication import Publication
from app.models.Skill import Skill
from app.models.Tool import Tool


def _save_profile(db: Session, user_id: str, resume_url: str, data: dict) -> Profile:
    p = data.get("profile", {})
    links = p.get("links") or {}

    profile = Profile(
        userId=user_id,
        full_name=p.get("full_name") or "Unknown",
        headline=p.get("headline"),
        summary=p.get("summary"),
        resume_link=resume_url,
        cover_letter_link=None,
        links=links if any(links.values()) else None,
    )

    db.add(profile)
    db.flush()
    return profile


def _save_experience(db: Session, profile_id: str, items: list):
    for i, item in enumerate(items or [], start=1):
        exp = Experience(
            profileId=profile_id,
            company_name=item.get("company_name") or "Unknown",
            role=item.get("role") or "Unknown",
            employment_type=item.get("employment_type") or "full_time",
            location_type=item.get("location_type") or "onsite",
            location_details=item.get("location_details"),
            description=item.get("description"),
            techStack=item.get("techStack") or [],
            start_month=item.get("start_month"),
            start_year=item.get("start_year"),
            end_month=item.get("end_month"),
            end_year=item.get("end_year"),
            priority=item.get("priority") or i,
        )
        db.add(exp)


def _save_academics(db: Session, profile_id: str, items: list):
    for item in items or []:
        academic = Academic(
            profileId=profile_id,
            degree_name=item.get("degree_name") or "Unknown",
            college_name=item.get("college_name") or "Unknown",
            description=item.get("description"),
            links=item.get("links") or {},
            start_month=item.get("start_month"),
            start_year=item.get("start_year"),
            end_month=item.get("end_month"),
            end_year=item.get("end_year"),
        )
        db.add(academic)


def _save_achievments(db: Session, profile_id: str, items: list):
    for item in items or []:
        achievement = Achievement(
            profileId=profile_id,
            title=item.get("title") or "Unknown",
            achievement_type=item.get("achievement_type") or "other",
            description=item.get("description"),
            location=item.get("location"),
            start_month=item.get("start_month"),
            start_year=item.get("start_year"),
            end_month=item.get("end_month"),
            end_year=item.get("end_year"),
            links=item.get("links") or {},
        )
        db.add(achievement)


def _save_projects(db: Session, profile_id: str, items: list):
    for item in items or []:
        project = Project(
            profileId=profile_id,
            title=item.get("title") or "Untitled Project",
            description=item.get("description"),
            techStack=item.get("techStack") or [],
            links=item.get("links") or {},
            startDate=item.get("startDate"),
            endDate=item.get("endDate"),
        )
        db.add(project)


def _save_publications(db: Session, profile_id, items: list):
    for item in items or []:
        publication = Publication(
            profileId=profile_id,
            title=item.get("title") or "Untitled",
            publisher=item.get("publisher"),
            publication_date=item.get("publication_date"),
            authors=item.get("authors") or [],
            description=item.get("description"),
            url=item.get("url"),
        )
        db.add(publication)


def _save_skills(
    db: Session, user_id: str, profile_id: str, skill_names: list[str]
) -> list[Skill]:
    saved = []
    for name in skill_names or []:
        name = name.strip().lower()
        if not name:
            continue
        existing = db.query(Skill).filter(Skill.name == name).first()
        if existing:
            saved.append(existing)
        else:
            skill = Skill(name=name, created_by=user_id)
            db.add(skill)
            db.flush()
            saved.append(skill)
    return saved


def _save_tools(db: Session, user_id, profile_id, tool_names: list) -> list[Tool]:
    """
    Tools are global (unique by name). Reuse existing ones.
    """
    saved = []
    for name in tool_names or []:
        name = name.strip().lower()
        if not name:
            continue
        existing = db.query(Tool).filter(Tool.name == name).first()
        if existing:
            saved.append(existing)
        else:
            tool = Tool(name=name, created_by=user_id)
            db.add(tool)
            db.flush()
            saved.append(tool)
    return saved
