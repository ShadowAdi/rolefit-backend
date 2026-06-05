import re
from typing import Optional, Dict, Any
from pydantic import field_validator, BaseModel
from enum import Enum
from pydantic import BaseModel, ConfigDict


class ProviderTypeEnumType(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"
    OTHER = "other"


class ApiKeyValidator(BaseModel):
    """Validators for ApiKey model"""

    PROVIDER_KEY_PATTERNS = {
        ProviderTypeEnumType.GROQ: r"^gsk_[A-Za-z0-9]{32,}$",
        ProviderTypeEnumType.OPENAI: r"^sk-[A-Za-z0-9]{20,}$",
        ProviderTypeEnumType.ANTHROPIC: r"^sk-ant-[A-Za-z0-9_-]{20,}$",
        ProviderTypeEnumType.GOOGLE: r"^AIza[A-Za-z0-9_-]{20,}$",
        ProviderTypeEnumType.COHERE: r"^[A-Za-z0-9]{20,}$",
        ProviderTypeEnumType.MISTRAL: r"^[A-Za-z0-9]{20,}$",
    }

    PROVIDER_BASE_URLS = {
        ProviderTypeEnumType.GROQ: [
            "https://api.groq.com",
            "https://api.groq.com/openai",
        ],
        ProviderTypeEnumType.OPENAI: [
            "https://api.openai.com",
            "https://api.openai.com/v1",
        ],
        ProviderTypeEnumType.ANTHROPIC: ["https://api.anthropic.com"],
        ProviderTypeEnumType.GOOGLE: ["https://generativelanguage.googleapis.com"],
        ProviderTypeEnumType.COHERE: ["https://api.cohere.ai"],
        ProviderTypeEnumType.MISTRAL: ["https://api.mistral.ai"],
    }

    @staticmethod
    def validate_key_name(v: str) -> str:
        """Validate API key name (user-friendly label)"""
        if not v or not v.strip():
            raise ValueError("Key name cannot be empty")

        if len(v) < 3:
            raise ValueError("Key name must be at least 3 characters long")

        if len(v) > 100:
            raise ValueError("Key name must not exceed 100 characters")

        v = v.strip()

        if not re.match(r"^[a-zA-Z0-9\s\-_()]+$", v):
            raise ValueError(
                "Key name contains invalid characters. Use alphanumeric, spaces, hyphens, underscores, and parentheses."
            )

        return v

    @staticmethod
    def validate_key_value(
        v: str, provider: Optional[ProviderTypeEnumType] = None
    ) -> str:
        """Validate the actual API key value"""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")

        v = v.strip()

        if len(v) < 10:
            raise ValueError(
                "API key is too short. Most API keys are at least 10 characters."
            )

        if len(v) > 500:
            raise ValueError("API key exceeds maximum length of 500 characters")

        if " " in v:
            raise ValueError("API key should not contain spaces")

        if "\n" in v or "\r" in v:
            raise ValueError("API key should not contain line breaks")

        if provider and provider in ApiKeyValidator.PROVIDER_KEY_PATTERNS:
            pattern = ApiKeyValidator.PROVIDER_KEY_PATTERNS[provider]
            if not re.match(pattern, v):
                raise ValueError(
                    f"Invalid {provider.value} API key format. "
                    f"Expected format: {pattern}"
                )

        return v

    @staticmethod
    def validate_provider(v: ProviderTypeEnumType) -> ProviderTypeEnumType:
        """Validate provider type"""
        if not v:
            raise ValueError("Provider type is required")

        if not isinstance(v, ProviderTypeEnumType):
            try:
                v = ProviderTypeEnumType(v)
            except ValueError:
                raise ValueError(
                    f"Invalid provider. Must be one of: {[p.value for p in ProviderTypeEnumType]}"
                )

        return v

    @staticmethod
    def validate_api_base_url(
        v: Optional[str], provider: Optional[ProviderTypeEnumType] = None
    ) -> Optional[str]:
        """Validate API base URL if provided"""
        if v is None:
            return v

        if not v or not v.strip():
            return None

        v = v.strip()

        url_pattern = r"^https?://[a-zA-Z0-9\-\.]+(?::\d+)?(?:/[a-zA-Z0-9\-\._~:/?#\[\]@!$&'()*+,;=]*)?$"
        if not re.match(url_pattern, v):
            raise ValueError("Invalid URL format. Must start with http:// or https://")

        if provider and provider in ApiKeyValidator.PROVIDER_BASE_URLS:
            is_valid_pattern = any(
                v.startswith(base_url)
                for base_url in ApiKeyValidator.PROVIDER_BASE_URLS[provider]
            )
            if not is_valid_pattern:
                expected_urls = ", ".join(ApiKeyValidator.PROVIDER_BASE_URLS[provider])
                raise ValueError(
                    f"For {provider.value}, API base URL should typically start with: {expected_urls}"
                )

        if v.endswith("/"):
            v = v[:-1]

        return v

    @staticmethod
    def validate_api_version(v: Optional[str]) -> Optional[str]:
        """Validate API version"""
        if v is None:
            return v

        if not v or not v.strip():
            return None

        v = v.strip()

        version_pattern = r"^v?\d+(?:\.\d+)*(?:[-_]\d{4}-\d{2}-\d{2})?$"
        if not re.match(version_pattern, v):
            raise ValueError(
                "Invalid API version format. Examples: v1, v1.0, 2023-01-01, 1.0.0"
            )

        return v

    @staticmethod
    def validate_is_active(v: Optional[bool]) -> bool:
        """Validate is_active flag"""
        if v is None:
            return True
        return v

    @staticmethod
    def validate_key_uniqueness(
        user_id: str,
        provider: ProviderTypeEnumType,
        existing_keys: Optional[list] = None,
    ) -> bool:
        """Check if user already has an active key for this provider

        Args:
            user_id: User ID
            provider: Provider type
            existing_keys: List of existing API keys for the user

        Returns:
            True if unique for the user-provider combination

        Raises:
            ValueError: If user already has an active key for this provider
        """
        if not existing_keys:
            return True

        for key in existing_keys:
            if key.provider == provider and key.is_active:
                raise ValueError(
                    f"User already has an active {provider.value} API key. "
                    f"Please deactivate the existing key first or update it instead."
                )

        return True

    @staticmethod
    def validate_expiry_format(expires_at: Optional[str]) -> Optional[str]:
        """Validate expiry date format"""
        if not expires_at:
            return None

        date_pattern = r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d{3})?)?$"
        if not re.match(date_pattern, expires_at):
            raise ValueError(
                "Invalid date format. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
            )

        return expires_at

    @staticmethod
    def sanitize_key_value_for_logging(key_value: str) -> str:
        """Mask API key for logging purposes"""
        if not key_value:
            return "***"

        if len(key_value) <= 8:
            return "*" * len(key_value)

        return f"{key_value[:4]}...{key_value[-4:]}"

    @staticmethod
    def validate_rate_limit_metadata(
        metadata: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Validate optional metadata like rate limits"""
        if not metadata:
            return metadata

        allowed_keys = {"rate_limit_per_minute", "rate_limit_per_day", "notes"}

        for key in metadata.keys():
            if key not in allowed_keys:
                raise ValueError(
                    f"Invalid metadata key: {key}. Allowed: {', '.join(allowed_keys)}"
                )

        if "rate_limit_per_minute" in metadata:
            rl = metadata["rate_limit_per_minute"]
            if not isinstance(rl, int) or rl < 1 or rl > 10000:
                raise ValueError(
                    "rate_limit_per_minute must be an integer between 1 and 10000"
                )

        if "rate_limit_per_day" in metadata:
            rl = metadata["rate_limit_per_day"]
            if not isinstance(rl, int) or rl < 1 or rl > 1000000:
                raise ValueError(
                    "rate_limit_per_day must be an integer between 1 and 1000000"
                )

        return metadata
