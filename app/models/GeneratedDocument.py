from app.db.db import Base
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import timezone, datetime
import uuid
import enum


class GeneratedDocumentEnumType(str, enum.Enum):
    RESUME = "Resume"
    COVER_LETTER = "Cover-letter"


class GeneratedDocumment(Base):
    __tablename__ = "GeneratedDocument"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    jobId = Column(UUID, ForeignKey("JobDescription.id"), nullable=False)
    resume_text = Column(String, nullable=False)
    gen_doc_type = Column(
        SQLEnum(GeneratedDocumentEnumType),
        nullable=True,
        default=GeneratedDocumentEnumType.RESUME,
        index=True,
    )
    user_specifications = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
