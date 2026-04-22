from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.JobDescription import JobDescription
from app.models.User import User
from app.core.logger import logger
from uuid import UUID
from app.helpers.filter_jd import filter_jd


class ContentServiceClass:
    def generate_content(
        self,
        userId: str,
        jobId: str,
        db: Session,
    ):
        try:
            logger.info(f"Starting experience creation process for user: {userId}")

            if not userId or not jobId:
                logger.error("Failed to generate content. No user id and job id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to generate content.",
                )

            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Generate Content Failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            jd = (
                db.query(JobDescription)
                .filter(
                    JobDescription.id == UUID(jobId),
                    JobDescription.userId == UUID(userId),
                )
                .first()
            )

            if not jd:
                logger.warning(
                    f"JD not found",
                    extra={"userId": userId, "jd_id": jobId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found",
                )

            filter_jd(jobId=jd.id, userId=user.id, db=db)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This experience may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating experience.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during experience creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the experience.",
            )
