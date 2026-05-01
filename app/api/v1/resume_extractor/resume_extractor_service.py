from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from app.models.User import User
from app.core.logger import logger
from app.core.AppError import AppError
from urllib.parse import urlparse
from app.utils.extract_resume_content import extract_resume_content
from app.utils.call_groq import _call_groq
from app.helpers.db_helpers import (
    _save_academics,
    _save_achievments,
    _save_experience,
    _save_profile,
    _save_projects,
    _save_publications,
    _save_skills,
    _save_tools,
)


class ResumeExtractorServiceClass:
    async def resumeextractor(self, db: Session, resume_url: str, userId: str):
        if not userId:
            logger.error(
                f"Project creation failed: Missing user ID",
                extra={"userId": userId},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID is required",
            )
        try:
            if not resume_url or not resume_url.strip():
                logger.error(
                    "Resume extraction failed: missing resume URL",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="resume_url is required",
                )

            parsed = urlparse(resume_url.strip())
            if parsed.scheme not in ("http", "https"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="resume_url must be an http or https URL",
                )

            logger.info(
                f"Resume URL validated for user {userId}", extra={"userId": userId}
            )

            extracted = await extract_resume_content(resume_url=resume_url.strip())

            logger.info(
                f"Resume content extracted for user {userId}", extra={"userId": userId}
            )

            resume_text: str = extracted["raw_text"]
            pdf_links: list[str] = extracted["links"]

            logger.info(
                f"PDF extracted for user {userId}: "
                f"{extracted['page_count']} pages, {len(resume_text)} chars"
            )

            groq_data = await _call_groq(
                resume_text=resume_text,
                extracted_links=pdf_links,
                resume_url=resume_url.strip(),
            )

            logger.info(
                f"Groq AI data processed for user {userId}", extra={"userId": userId}
            )

            profile = _save_profile(db, userId, resume_url.strip(), groq_data)

            logger.info(f"Profile saved for user {userId}", extra={"userId": userId})

            experience_items = groq_data.get("experience") or []
            academic_items = groq_data.get("academics") or []
            achievement_items = groq_data.get("achievements") or []
            project_items = groq_data.get("projects") or []
            publication_items = groq_data.get("publications") or []
            skill_names = groq_data.get("skills") or []
            tool_names = groq_data.get("tools") or []

            _save_experience(db, profile.id, experience_items)
            _save_academics(db, profile.id, academic_items)
            _save_achievments(db, profile.id, achievement_items)
            _save_projects(db, profile.id, project_items)
            _save_publications(db, profile.id, publication_items)

            saved_skills = _save_skills(db, userId, profile.id, skill_names)
            saved_tools = _save_tools(db, userId, profile.id, tool_names)

            db.commit()
            db.refresh(profile)

            logger.info(
                f"Resume import completed for user {userId}: "
                f"profile={profile.id}, "
                f"exp={len(experience_items)}, "
                f"academic={len(academic_items)}, "
                f"achievement={len(achievement_items)}, "
                f"project={len(project_items)}, "
                f"publication={len(publication_items)}, "
                f"skills={len(saved_skills)}, "
                f"tools={len(saved_tools)}",
                extra={"userId": userId, "profileId": str(profile.id)},
            )

            return {
                "profile_id": str(profile.id),
                "counts": {
                    "experience": len(experience_items),
                    "academics": len(academic_items),
                    "achievements": len(achievement_items),
                    "projects": len(project_items),
                    "publications": len(publication_items),
                    "skills": len(saved_skills),
                    "tools": len(saved_tools),
                },
            }

        except HTTPException:
            raise

        except AppError as e:
            logger.error(f"App config error during resume import: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error during resume import for user {userId}: {e}",
                extra={"userId": userId, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation during resume import.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during resume import for user {userId}: {e}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during resume import.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during resume import for user {userId}: {e}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during resume import.",
            )
