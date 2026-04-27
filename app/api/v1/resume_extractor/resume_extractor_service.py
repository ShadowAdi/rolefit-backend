from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from app.models.User import User
from app.core.logger import logger
from app.core.AppError import AppError
from urllib.parse import urlparse
from app.utils.extract_resume_content import extract_resume_content
from app.models.Profile import Profile
from app.utils.call_sarvam import _call_sarvam
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
    def resumeextractor(self, db: Session, resume_url: str, userId: str):
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

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            existing_profile = (
                db.query(Profile).filter(Profile.userId == userId).first()
            )
            if existing_profile:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A profile already exists for this user. "
                        "Use the PATCH endpoint to update it, or use the individual "
                        "endpoints to add experience, projects, etc."
                    ),
                )

            parsed = urlparse(resume_url.strip())
            if parsed.scheme not in ("http", "https"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="resume_url must be an http or https URL",
                )

            extracted = extract_resume_content(resume_url=resume_url.strip())

            resume_text: str = extracted["raw_text"]
            pdf_links: list[str] = extracted["links"]

            logger.info(
                f"PDF extracted for user {userId}: "
                f"{extracted['page_count']} pages, {len(resume_text)} chars"
            )

            sarvam_data = _call_sarvam(
                resume_text=resume_text, extracted_links=pdf_links
            )

            profile = _save_profile(db, userId, resume_url.strip(), sarvam_data)

            experience_items = sarvam_data.get("experience") or []
            academic_items = sarvam_data.get("academics") or []
            achievement_items = sarvam_data.get("achievements") or []
            project_items = sarvam_data.get("projects") or []
            publication_items = sarvam_data.get("publications") or []
            skill_names = sarvam_data.get("skills") or []
            tool_names = sarvam_data.get("tools") or []

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
            # sarvam_api_key_headers() raises this if API key is missing
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
