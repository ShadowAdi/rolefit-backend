from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Publication(Base):
    __tablename__ = "Publication"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    authors = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    profileId = Column(UUID, ForeignKey("Profile.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
