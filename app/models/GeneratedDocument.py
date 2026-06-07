from app.db.db import Base
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid
from app.models.ApiKeys import ProviderType
import enum


class GeneratedDocumentEnumType(str, enum.Enum):
    RESUME = "Resume"
    COVER_LETTER = "Cover-letter"


class GeneratedDocumentStatusEnumType(str, enum.Enum):
    Pending = "pending"
    Processing = "processing"
    Completed = "completed"
    failed = "failed"


class GeneratedDocumment(Base):
    __tablename__ = "GeneratedDocument"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    jobId = Column(UUID, ForeignKey("JobDescription.id"), nullable=False)
    resume_text = Column(String, nullable=True)
    cover_letter_text = Column(String, nullable=True)
    gen_doc_type = Column(
        SQLEnum(GeneratedDocumentEnumType),
        nullable=False,
        default=GeneratedDocumentEnumType.RESUME,
        index=True,
    )
    status = Column(
        SQLEnum(GeneratedDocumentStatusEnumType),
        nullable=False,
        default=GeneratedDocumentStatusEnumType.Pending,
        index=True,
    )
    error_message = Column(String, nullable=True)
    provider_used = Column(
        SQLEnum(ProviderType),
        nullable=True,
    )
    user_specifications = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
