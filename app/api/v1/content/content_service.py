import re
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.User import User
from app.core.logger import logger
from app.helpers.filter_jd import filter_jd
from app.models.GeneratedDocument import GeneratedDocumment, GeneratedDocumentEnumType
from app.response.GenerateDocument_responses import (
    GeneratedDocumnetResponse,
    DeleteDocumnetResponse,
)
from app.tasks.ai_tasks import generate_resume_task, generate_cover_letter_task
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache
from uuid import UUID
from app.models.ApiKeys import ProviderType


class ContentServiceClass:
    async def generate_resume_content(
        self,
        userId: str,
        jobId: str,
        user_specifications: str,
        db: Session,
        provider: str,
    ):
        try:
            logger.info(f"Starting resume generation for user: {userId}")

            if not userId or not jobId:
                logger.error("Failed to generate content. No user id and job id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to generate content.",
                )

            existing = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.jobId == jobId,
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.gen_doc_type == "Resume",
                )
                .count()
            )

            if existing >= 3:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A single job can't have more than 3 generated resumes. Delete one first.",
                )

            gen_doc = GeneratedDocumment(
                userId=UUID(userId),
                jobId=UUID(jobId),
                user_specifications=user_specifications,
                resume_text=None,
                gen_doc_type="Resume",
                status="pending",
                provider_used=ProviderType(provider.lower()) if provider else None,
            )
            db.add(gen_doc)
            db.commit()
            db.refresh(gen_doc)

            doc_id = str(gen_doc.id)

            job_profile_cache_key = f"job-profile-{jobId}-{userId}"
            cached_profile = await get_cache(job_profile_cache_key)
            if cached_profile:
                logger.info(f"Job profile retrieved from cache for jobId={jobId}")
                job_profile_response = json.loads(cached_profile)
            else:
                job_profile_response = await filter_jd(
                    jobId=jobId, userId=userId, db=db, content_type="Resume"
                )
                await set_cache(
                    job_profile_cache_key, json.dumps(job_profile_response), ttl=21600
                )

            task = generate_resume_task.delay(
                doc_id=doc_id,
                user_id=userId,
                job_id=jobId,
                user_specifications=user_specifications or "",
                provider=provider,
            )

            logger.info(f"Resume task queued | doc={doc_id} celery_task={task.id}")

            return {
                "doc_id": doc_id,
                "task_id": task.id,
                "status": "pending",
                "message": "Resume generation queued. Poll /status/{doc_id} for updates.",
            }

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for user={userId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating resume content.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the resume content.",
            )

    def get_all_user_contents(
        self,
        userId: str,
        content_type: GeneratedDocumentEnumType,
        db: Session,
    ):
        """Get all generated content for user across all JDs"""
        try:
            if not userId:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User ID is required",
                )

            query = db.query(GeneratedDocumment).filter(
                GeneratedDocumment.userId == userId,
            )

            if content_type:
                query = query.filter(GeneratedDocumment.gen_doc_type == content_type)

            genDocs = query.all()

            if not genDocs:
                return []

            return [
                GeneratedDocumnetResponse.model_validate(genDoc) for genDoc in genDocs
            ]

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for fetching all user content for user={userId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching contents.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching contents.",
            )

    def get_all_contents(
        self,
        userId: str,
        jobId: str,
        content_type: GeneratedDocumentEnumType,
        db: Session,
    ):
        try:
            if not userId or not jobId:
                logger.error("Failed to fetch all content. No user id and job id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch all content.",
                )

            query = db.query(GeneratedDocumment).filter(
                GeneratedDocumment.userId == userId,
                GeneratedDocumment.jobId == jobId,
            )

            if content_type:
                query = query.filter(GeneratedDocumment.gen_doc_type == content_type)

            genDocs = query.all()

            if not genDocs:
                logger.info(f"No content found for jobId={jobId}, userId={userId}")
                return []

            return [
                GeneratedDocumnetResponse.model_validate(genDoc) for genDoc in genDocs
            ]

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for fetching a;ll content={userId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching contents.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching contents.",
            )

    def get_content(
        self,
        userId: str,
        contentId: str,
        db: Session,
    ):
        try:

            if not userId or not contentId:
                logger.error("Failed to fetch content. No user id and content id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to fetch content by id {contentId}.",
                )

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(f"User not found: {userId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            genDoc = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.id == contentId,
                )
                .first()
            )

            if not genDoc:
                logger.warning(f"Content not found: {contentId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found",
                )

            return GeneratedDocumnetResponse.model_validate(genDoc)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for fetching content={contentId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching contents.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching content.",
            )

    def delete_content(
        self,
        userId: str,
        contentId: str,
        db: Session,
    ):
        try:
            if not userId or not contentId:
                logger.error("Failed to fetch content. No user id and content id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to fetch content by id {contentId}.",
                )

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(f"User not found: {userId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            docQuery = db.query(GeneratedDocumment).filter(
                GeneratedDocumment.userId == userId,
                GeneratedDocumment.id == contentId,
            )

            docFound = docQuery.first()

            if not docFound:
                logger.warning(
                    f"Content deletion failed: Content not found",
                    extra={"userId": userId, "contentId": contentId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found",
                )

            docFoundId = docFound.id
            docJobId = docFound.jobId

            db.delete(docFound)
            db.commit()

            # Invalidate job profile cache when content is deleted (in case we delete all content)
            job_profile_cache_key = f"job-profile-{docJobId}-{userId}"
            delete_cache(job_profile_cache_key)
            logger.debug(f"Invalidated job profile cache for jobId={docJobId}")

            return DeleteDocumnetResponse.model_validate(
                {
                    "message": f"Doc Id '{docFoundId}' has been successfully deleted",
                    "id": str(docFoundId),
                    "success": True,
                }
            )

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for deleting content content={contentId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting content.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting content.",
            )

    def get_document_status(
        self,
        doc_id: str,
        userId: str,
        db: Session,
    ):
        try:
            if not doc_id or not userId:
                logger.error("Failed to fetch document status. No doc id and user id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch document status.",
                )

            doc = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.id == doc_id,
                    GeneratedDocumment.userId == userId,
                )
                .first()
            )

            if not doc:
                logger.warning(f"Document not found: {doc_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found.",
                )

            response = {
                "doc_id": doc_id,
                "status": doc.status,
                "type": doc.gen_doc_type,
            }

            if doc.status == "failed" and getattr(doc, "error", None):
                response["error"] = doc.error

            return response

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for fetching document status doc={doc_id}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching document status.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while fetching document status.",
            )

    async def generate_cover_letter_content(
        self,
        userId: str,
        jobId: str,
        user_specifications: str,
        db: Session,
        provider: str = None,
    ):
        try:
            logger.info(f"Starting cover letter generation for user: {userId}")

            existing = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.jobId == jobId,
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.gen_doc_type == "Cover-letter",
                )
                .count()
            )
            if existing >= 3:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A single job can't have more than 3 generated cover letters. Delete one first.",
                )

            job_profile_cache_key = f"job-profile-{jobId}-{userId}"
            cached_profile = await get_cache(job_profile_cache_key)
            if cached_profile:
                logger.info(f"Job profile retrieved from cache for jobId={jobId}")
                job_profile_response = json.loads(cached_profile)
            else:
                job_profile_response = await filter_jd(
                    jobId=jobId, userId=userId, db=db, content_type="cover_letter"
                )
                await set_cache(
                    job_profile_cache_key, json.dumps(job_profile_response), ttl=21600
                )

            gen_doc = GeneratedDocumment(
                userId=UUID(userId),
                jobId=UUID(jobId),
                user_specifications=user_specifications,
                cover_letter_text=None,
                gen_doc_type="Cover-letter",
                status="pending",
                provider_used=ProviderType(provider.lower()) if provider else None,
            )
            db.add(gen_doc)
            db.commit()
            db.refresh(gen_doc)

            doc_id = str(gen_doc.id)

            task = generate_cover_letter_task.delay(
                doc_id=doc_id,
                user_id=userId,
                job_id=jobId,
                user_specifications=user_specifications or "",
                provider=provider,
            )

            logger.info(
                f"Cover letter task queued | doc={doc_id} celery_task={task.id}"
            )

            return {
                "doc_id": doc_id,
                "task_id": task.id,
                "status": "pending",
                "message": "Cover letter generation queued. Poll /status/{doc_id} for updates.",
            }

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"DB integrity error for user={userId}",
                extra={"error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"DB error for user={userId}",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating cover letter content.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error for user={userId}",
                extra={"error": str(e), "errorType": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the cover letter content.",
            )
