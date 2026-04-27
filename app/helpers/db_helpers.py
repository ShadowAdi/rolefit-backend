from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from app.core.logger import logger
from app.core.AppError import AppError

from app.models.User import User
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
