import os
from app.core.logger import logger
from app.core.AppError import AppError


def grok_api_key_headers() -> dict:
    try:
        logger.debug("Attempting to retrieve Grok AI api key")

        GROK_AI_API_KEY = os.getenv("GROK_AI_API_KEY")

        if not GROK_AI_API_KEY:
            logger.error("GROK_AI_API_KEY environment variable is not set")
            raise AppError(
                "GROK_AI_API_KEY environment variable is required but not set"
            )

        if not isinstance(GROK_AI_API_KEY, str) or len(GROK_AI_API_KEY.strip()) == 0:
            logger.error("GROK_AI_API_KEY is empty or invalid")
            raise AppError("GROK_AI_API_KEY must be a non-empty string")

        logger.info("Sarvam AI headers created successfully")
        return GROK_AI_API_KEY

    except AppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in grok headers: {str(e)}")
        raise AppError(f"Error creating grok headers: {str(e)}")
