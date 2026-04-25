import re
import requests
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.JobDescription import JobDescription
from app.models.User import User
from app.core.logger import logger
from app.helpers.filter_jd import filter_jd
from app.helpers.resume_prompt import build_resume_prompt
from app.utils.sarvam_const import MAX_TOKENS, RESUME_GEN_TIMEOUT, SARVAM_API_URL
from app.helpers.sarvam_ai_headers import sarvam_api_key_headers
from app.models.GeneratedDocument import GeneratedDocumment
from app.response.GenerateDocument_responses import GenerateDocCreateResponse
from uuid import UUID


def _extract_clean_json(raw: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in AI response")

    candidate = match.group()

    candidate = match.group()

    json.loads(candidate)

    return candidate


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
                    JobDescription.id == jobId,
                    JobDescription.userId == userId,
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

            job_profile_response = filter_jd(
                jobId=str(jd.id), userId=str(user.id), db=db
            )

            headers = sarvam_api_key_headers()

            prompt = build_resume_prompt(job_profile_response)

            payload = {
                "model": "sarvam-m",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": MAX_TOKENS,
            }

            logger.debug(f"Calling Sarvam AI API for resume generation")

            response = requests.post(
                SARVAM_API_URL,
                json=payload,
                headers=headers,
                timeout=RESUME_GEN_TIMEOUT,
            )

            response.raise_for_status()

            response_data = response.json()

            if "choices" not in response_data or len(response_data["choices"]) == 0:
                logger.error(
                    "Invalid API response: No choices in response",
                    extra={"response": response_data},
                )
                raise ValueError("Invalid response from AI API")

            message_content = (
                response_data["choices"][0].get("message", {}).get("content", "")
            )

            if not message_content:
                logger.error(
                    "Invalid API response: No message content",
                    extra={"response": response_data},
                )
                raise ValueError("No content in API response")

            clean = re.sub(
                r"<think>.*?</think>", "", message_content, flags=re.DOTALL
            ).strip()

            logger.debug(
                f"Successfully generated resume text",
                extra={"userId": userId, "jobId": jobId},
            )

            if not clean:
                logger.error(f"Failed to parse the clean resume documnet")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to generate resume content",
                )

            genDoc = GeneratedDocumment(
                userId=UUID(userId), jobId=UUID(jobId), resume_text=clean
            )

            db.add(genDoc)
            db.commit()
            db.refresh(genDoc)

            return GenerateDocCreateResponse.model_validate(genDoc)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during resume content creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during resume content creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while  resume content creation.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during resume creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the resume content.",
            )
