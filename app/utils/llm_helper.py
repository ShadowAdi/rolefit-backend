import json
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.ApiKeys import ProviderType
from app.api.v1.llm.llm_factory import LLMServiceFactory
from app.core.logger import logger
from app.helpers.redis_cache_helpers import get_cache, set_cache


class LLMHelper:
    """Helper class to make LLM calls with user's API keys"""

    def __init__(
        self, db: Session, user_id: str, provider: Optional[ProviderType] = None
    ):
        self.db = db
        self.user_id = user_id
        self.provider = provider

    async def get_llm_service(self):
        """Get or create LLM service for the user"""
        from app.api.v1.llm.llm_factory import LLMServiceFactory

        if not self.provider:
            # Get default provider
            self.provider = await LLMServiceFactory.get_default_provider_for_user(
                self.db, self.user_id
            )
            if not self.provider:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No API key configured. Please add an API key first.",
                )

        return await LLMServiceFactory.get_llm_service(
            self.db, self.user_id, self.provider
        )

    async def call_with_prompt(
        self,
        prompt: str,
        system_prompt: str = None,
        use_cache: bool = False,
        cache_key: str = None,
        cache_ttl: int = 86400,
        **kwargs,
    ) -> str:
        """Make LLM call with optional caching"""

        # Check cache if enabled
        if use_cache and cache_key:
            try:
                cached = await get_cache(cache_key)
                if cached:
                    logger.info(f"Cache HIT for key {cache_key}")
                    return cached
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Get LLM service and make call
        llm_service = await self.get_llm_service()
        response = await llm_service.call_llm(prompt, system_prompt, **kwargs)

        # Store in cache if enabled
        if use_cache and cache_key and response:
            try:
                await set_cache(cache_key, response, ttl=cache_ttl)
                logger.info(f"Cached response for key {cache_key}")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

        return response

    async def call_with_json_response(
        self,
        prompt: str,
        system_prompt: str = None,
        use_cache: bool = False,
        cache_key: str = None,
        **kwargs,
    ) -> dict:
        """Make LLM call and parse JSON response"""
        from app.utils.extract_clean_json_content import _extract_clean_json

        response = await self.call_with_prompt(
            prompt, system_prompt, use_cache, cache_key, **kwargs
        )

        try:
            return _extract_clean_json(response)
        except ValueError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM service did not return valid JSON.",
            )
