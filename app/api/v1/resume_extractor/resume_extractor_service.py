from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from app.models.User import User
from app.core.logger import logger
from urllib.parse import urlparse
from app.utils.extract_resume_content import extract_resume_content


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

            parsed = urlparse(resume_url.strip())
            if parsed.scheme not in ("http", "https"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="resume_url must be an http or https URL",
                )

            result = extract_resume_content(resume_url=resume_url.strip())
            logger.info(
                f"Resume extraction successful for user {userId}: "
                f"{result['page_count']} pages, {len(result['raw_text'])} chars",
                extra={"userId": userId},
            )
            return result

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error during resume extraction for user {userId}: {e}",
                extra={"userId": userId, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during resume extraction for user {userId}: {e}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during resume extraction for user {userId}: {e}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while extracting resume content",
            )
