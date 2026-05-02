import re
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.JobDescription import JobDescription
from app.models.User import User
from app.core.logger import logger
from app.helpers.filter_jd import filter_jd
from app.helpers.resume_prompt import build_resume_prompt
from app.helpers.cover_letter_prompt import _build_cover_letter_prompt
from app.models.GeneratedDocument import GeneratedDocumment, GeneratedDocumentEnumType
from app.response.GenerateDocument_responses import (
    GenerateDocCreateResponse,
    GeneratedDocumnetResponse,
    DeleteDocumnetResponse,
)
from app.tasks.ai_tasks import generate_resume_task, generate_cover_letter_task
from app.helpers.grok_ai_headers import grok_api_key_headers
from app.helpers.redis_cache_helpers import get_cache, set_cache, delete_cache
from app.utils.extract_clean_json_content import _extract_clean_json
from uuid import UUID
from groq import Groq


class ContentServiceClass:
    async def generate_resume_content(
        self,
        userId: str,
        jobId: str,
        user_specifications: str,
        db: Session,
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

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(f"User not found: {userId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            genDocs = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.jobId == jobId,
                    GeneratedDocumment.gen_doc_type == content_type,
                )
                .all()
            )

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

    async def generate_cover_letter_content(
        self,
        userId: str,
        jobId: str,
        user_specifications: str,
        db: Session,
    ):
        try:
            logger.info(f"Starting cover letter generation for user: {userId}")

            # Try cache first for job profile
            job_profile_cache_key = f"job-profile-{jobId}-{userId}"
            cached_profile = await get_cache(job_profile_cache_key)
            if cached_profile:
                logger.info(f"Job profile retrieved from cache for jobId={jobId}")
                job_profile_response = json.loads(cached_profile)
            else:
                job_profile_response = await filter_jd(
                    jobId=jobId, userId=userId, db=db, content_type="cover_letter"
                )
                # Cache job profile for 6 hours (won't change unless JD is updated)
                await set_cache(
                    job_profile_cache_key, json.dumps(job_profile_response), ttl=21600
                )

            genDocs = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.jobId == jobId,
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.gen_doc_type == "Cover-letter",
                )
                .all()
            )
            if len(genDocs) > 3:
                logger.error("One Job cant have more than 3 Docs")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A Single Job cant have more than 3 Generated Content. Delete the previous or use already existing ones to generate cover letter",
                )

            logger.info(f"User verified: {userId}")

            prompt = _build_cover_letter_prompt(
                job_profile_response, user_specifications
            )

            logger.debug("Calling Groq API for cover letter generation")

            api_key = grok_api_key_headers()
            groq_client = Groq(api_key=api_key)

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a JSON-only resume writer. "
                            "Output ONLY valid JSON. No markdown, no explanation, no extra text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=4000,
                temperature=0.3,
            )

            message_content = chat_completion.choices[0].message.content

            if not message_content:
                logger.error("Groq returned empty content")
                raise ValueError("No content in Groq API response")

            try:
                clean_json = _extract_clean_json(message_content)
            except (ValueError, json.JSONDecodeError) as e:
                logger.error(
                    f"Groq returned invalid JSON for user={userId} job={jobId}: {e}",
                    extra={"raw_response": message_content[:500]},
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "The AI returned an unexpected format. "
                        "Please try generating again."
                    ),
                )

            logger.debug(f"Cover letter JSON generated successfully for user={userId}")

            gen_doc = GeneratedDocumment(
                userId=UUID(userId),
                jobId=UUID(jobId),
                user_specifications=user_specifications,
                cover_letter_text=json.dumps(clean_json),
                gen_doc_type="Cover-letter",
                status="completed",
            )

            db.add(gen_doc)
            db.commit()
            db.refresh(gen_doc)

            return GenerateDocCreateResponse.model_validate(gen_doc)

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
