import os
from app.core.logger import logger
from app.core.AppError import AppError


def sarvam_api_key_headers() -> dict:
    try:
        logger.debug("Attempting to retrieve Sarvam AI api key")

        AI_API_KEY = os.getenv("AI_API_KEY")

        if not AI_API_KEY:
            logger.error("AI_API_KEY environment variable is not set")
            raise AppError("AI_API_KEY environment variable is required but not set")

        if not isinstance(AI_API_KEY, str) or len(AI_API_KEY.strip()) == 0:
            logger.error("AI_API_KEY is empty or invalid")
            raise AppError("AI_API_KEY must be a non-empty string")

        headers = {
            "api-subscription-key": AI_API_KEY,
            "Content-Type": "application/json",
        }

        logger.info("Sarvam AI headers created successfully")
        return headers

    except AppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in sarvam headers: {str(e)}")
        raise AppError(f"Error creating Sarvam headers: {str(e)}")
