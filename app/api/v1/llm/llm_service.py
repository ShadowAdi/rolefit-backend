from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.ApiKeys import ApiKey, ProviderType
from app.api.v1.apiKeys.apiKeys_service import ApiKeysServiceClass
from app.core.logger import logger
from app.helpers.api_key_encryption import api_key_encryption


class LLMService:
    def __init__(self, db: Session, user_id: str, provider: ProviderType):
        self.db = db
        self.user_id = user_id
        self.provider = provider
        self.api_keys_service = ApiKeysServiceClass()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        # Get the API key from database
        provider_value = (
            self.provider.value
            if hasattr(self.provider, "value")
            else str(self.provider)
        )

        logger.info(
            f"Looking for API key - User: {self.user_id}, Provider: {provider_value}"
        )

        api_key_record = (
            self.db.query(ApiKey)
            .filter(
                ApiKey.user_id == self.user_id,
                ApiKey.provider == provider_value,
                ApiKey.is_active == True,
            )
            .first()
        )

        if not api_key_record:
            logger.error(
                f"No active API key found for user {self.user_id}, provider {provider_value}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active API key found for provider {self.provider.value}",
            )

        logger.info(
            f"Found API key record: {api_key_record.id}, name: {api_key_record.key_name}"
        )

        # Get decrypted key
        decrypted_key = api_key_encryption.decrypt_api_key(api_key_record.key_value)

        # Log first/last few chars (safe)
        key_preview = (
            f"{decrypted_key[:10]}...{decrypted_key[-10:]}"
            if len(decrypted_key) > 20
            else "***"
        )
        logger.info(
            f"Decrypted API key for {self.provider.value}: {key_preview} (length: {len(decrypted_key)})"
        )

        # Validate the decrypted key looks correct
        if self.provider == ProviderType.GROQ and not decrypted_key.startswith("gsk_"):
            logger.error(
                f"Decrypted Groq key doesn't start with 'gsk_'! Got: {decrypted_key[:10]}..."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Decrypted API key format is incorrect. Please re-enter your API key.",
            )

        # Initialize client
        if self.provider == ProviderType.GROQ:
            from groq import Groq

            self.client = Groq(api_key=decrypted_key)
            logger.info(f"Groq client initialized successfully")

        elif self.provider == ProviderType.OPENAI:
            from openai import OpenAI

            self.client = OpenAI(api_key=decrypted_key)
        elif self.provider == ProviderType.ANTHROPIC:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=decrypted_key)
        elif self.provider == ProviderType.GOOGLE:
            import google.generativeai as genai

            genai.configure(api_key=decrypted_key)
            self.client = genai
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {self.provider.value}",
            )

    async def call_llm(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        try:
            if self.provider == ProviderType.GROQ:
                return await self._call_groq(prompt, system_prompt, **kwargs)
            elif self.provider == ProviderType.OPENAI:
                return await self._call_openai(prompt, system_prompt, **kwargs)
            elif self.provider == ProviderType.ANTHROPIC:
                return await self._call_anthropic(prompt, system_prompt, **kwargs)
            elif self.provider == ProviderType.GOOGLE:
                return await self._call_google(prompt, system_prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM call failed for {self.provider.value}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error calling {self.provider.value} API: {str(e)}",
            )

    async def _call_groq(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            messages=messages,
            model=kwargs.get("model", "llama-3.3-70b-versatile"),
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.1),
        )
        return response.choices[0].message.content

    async def _call_openai(
        self, prompt: str, system_prompt: str = None, **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            messages=messages,
            model=kwargs.get("model", "gpt-4"),
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.1),
        )
        return response.choices[0].message.content

    async def _call_anthropic(
        self, prompt: str, system_prompt: str = None, **kwargs
    ) -> str:
        response = self.client.messages.create(
            model=kwargs.get("model", "claude-3-sonnet-20240229"),
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.1),
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def _call_google(
        self, prompt: str, system_prompt: str = None, **kwargs
    ) -> str:
        model = self.client.GenerativeModel(kwargs.get("model", "gemini-pro"))
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = model.generate_content(full_prompt)
        return response.text

    # Add sync version for Celery tasks
    def call_llm_sync(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Synchronous version for Celery tasks"""
        import asyncio

        return asyncio.run(self.call_llm(prompt, system_prompt, **kwargs))
