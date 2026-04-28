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
from app.models.GeneratedDocument import GeneratedDocumment
from app.response.GenerateDocument_responses import (
    GenerateDocCreateResponse,
    GeneratedDocumnetResponse,
    DeleteDocumnetResponse,
)
from app.helpers.grok_ai_headers import grok_api_key_headers
from uuid import UUID
from groq import Groq

# --- Sarvam imports (commented out) ---
# import requests
# from app.utils.sarvam_const import (
#     RESUME_GEN_MAX_TOKENS,
#     RESUME_GEN_TIMEOUT,
#     SARVAM_API_URL,
# )
# from app.helpers.sarvam_ai_headers import sarvam_api_key_headers


def _extract_clean_json(text: str) -> dict:
    print(f"AI OUTPUT: {text}")

    # Strip <think> blocks (reasoning models)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Strip markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"\s*```$", "", text).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract valid JSON from model output")


class ContentServiceClass:
    def generate_resume_content(
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

            job_profile_response = filter_jd(
                jobId=jobId, userId=userId, db=db, content_type="Resume"
            )

            genDocs = (
                db.query(GeneratedDocumment)
                .filter(
                    GeneratedDocumment.jobId == jobId,
                    GeneratedDocumment.userId == userId,
                    GeneratedDocumment.gen_doc_type == "Resume",
                )
                .all()
            )
            if len(genDocs) > 3:
                logger.error("One Job cant have more than 3 Docs")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A Single Job cant have more than 3 Generated Content. Delete the previous or use already existing ones to generate resume",
                )

            prompt = build_resume_prompt(job_profile_response)

            # --- Sarvam API call (commented out) ---
            # headers = sarvam_api_key_headers()
            # payload = {
            #     "model": "sarvam-m",
            #     "messages": [
            #         {
            #             "role": "system",
            #             "content": "/no_think You are a JSON-only resume writer...",
            #         },
            #         {"role": "user", "content": prompt},
            #     ],
            #     "max_tokens": RESUME_GEN_MAX_TOKENS,
            # }
            # response = requests.post(
            #     SARVAM_API_URL,
            #     json=payload,
            #     headers=headers,
            #     timeout=RESUME_GEN_TIMEOUT,
            # )
            # response.raise_for_status()
            # response_data = response.json()
            # message_content = (
            #     response_data["choices"][0].get("message", {}).get("content", "")
            # )

            logger.debug("Calling Groq API for resume generation")

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
                temperature=0.3,  # lower = more deterministic JSON output
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

            logger.debug(f"Resume JSON generated successfully for user={userId}")

            gen_doc = GeneratedDocumment(
                userId=UUID(userId),
                jobId=UUID(jobId),
                user_specifications=user_specifications,
                resume_text=json.dumps(clean_json),
                gen_doc_type="Resume",
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

    def get_all_resume_contents(
        self,
        userId: str,
        jobId: str,
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

    def get_resume_content(
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

    def delete_resume_content(
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

            db.delete(docFound)
            db.commit()

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

    def generate_cover_letter_content(
        self,
        userId: str,
        jobId: str,
        user_specifications: str,
        db: Session,
    ):
        try:
            logger.info(f"Starting resume generation for user: {userId}")

            job_profile_response = filter_jd(
                jobId=jobId, userId=userId, db=db, content_type="cover_letter"
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

            prompt = build_resume_prompt(job_profile_response)

            logger.debug("Calling Groq API for resume generation")

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

            logger.debug(f"Resume JSON generated successfully for user={userId}")

            gen_doc = GeneratedDocumment(
                userId=UUID(userId),
                jobId=UUID(jobId),
                user_specifications=user_specifications,
                resume_text=json.dumps(clean_json),
                gen_doc_type="Cover-letter",
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
