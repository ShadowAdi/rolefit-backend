from typing import Optional
from sqlalchemy.orm import Session
from app.models.ApiKeys import ProviderType
from .llm_service import LLMService
from app.core.logger import logger


class LLMServiceFactory:
    @staticmethod
    async def get_llm_service(
        db: Session, user_id: str, provider: ProviderType
    ) -> LLMService:
        try:
            service = LLMService(db, user_id, provider)
            return service
        except Exception as e:
            logger.error(f"Failed to create LLM service: {str(e)}")
            raise

    @staticmethod
    async def get_default_provider_for_user(
        db: Session, user_id: str
    ) -> Optional[ProviderType]:
        """Get user's preferred/default provider (first active one)"""
        from app.models.ApiKeys import ApiKey

        api_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True,
                ApiKey.isDefault == True,
            )
            .first()
        )

        return api_key.provider if api_key else None
