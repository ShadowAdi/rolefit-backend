from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from app.models.User import User
from app.core.logger import logger
from typing import List


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
            if not resume_url:
                logger.error("Failed to get the resume url")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Failed to get the resume url",
                )

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
