from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.ApiKeys import ApiKey, ProviderType
from app.api.v1.apiKeys.apiKeys_service import ApiKeysServiceClass
from app.core.logger import logger
import json


class LLMService:
    def __init__(self, db: Session, user_id: str, provider: ProviderType):
        self.db = db
        self.userId = user_id
        self.provider = self.provider
        self.api_keys_service = ApiKeysServiceClass()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        api_key_record = (
            self.db.query(ApiKey)
            .filter(
                ApiKey.user_id == self.user_id,
                ApiKey.provider == self.provider,
                ApiKey.is_active == True,
            )
            .first()
        )

        if not api_key_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active API key found for provider {self.provider.value}",
            )

        decrypted_key = self.api_keys_service.get_decrypted_key_for_use(
            self.db, str(api_key_record.id), self.user_id
        )

        if self.provider == ProviderType.GROQ:
            from groq import Groq

            self.client = Groq(api_key=decrypted_key)
        elif self.provider == ProviderType.OPENAI:
            from openai import OpenAI

            self.client = OpenAI(api_key=decrypted_key)
            pass
        elif self.provider == ProviderType.ANTHROPIC:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=decrypted_key)
            pass
        elif self.provider == ProviderType.GOOGLE:
            import google.generativeai as genai

            genai.configure(api_key=decrypted_key)
            self.client = genai
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {self.provider.value}",
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

    async def _call_groq(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
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
