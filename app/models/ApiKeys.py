from app.db.db import Base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
    Boolean,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid
import enum


# Define supported providers as enum
class ProviderType(enum.Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Claude
    GOOGLE = "google"  # Gemini
    COHERE = "cohere"
    MISTRAL = "mistral"
    OTHER = "other"


class ApiKey(Base):
    __tablename__ = "ApiKeys"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    provider = Column(Enum(ProviderType), nullable=False, index=True)
    key_name = Column(String, nullable=False)
    key_value = Column(String, nullable=False)

    api_base_url = Column(String, nullable=True)
    api_version = Column(String, nullable=True)

    last_used_at = Column(DateTime, nullable=True)
    total_requests = Column(Integer, default=0)

    is_active = Column(Boolean, default=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    metadata = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_user_active_keys", "user_id", "provider", "is_active"),
    )
