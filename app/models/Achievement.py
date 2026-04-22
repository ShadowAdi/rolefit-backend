from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Achievement(Base):
    __tablename__ = "Achievement"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    achievement_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_month = Column(String, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_month = Column(String, nullable=True)
    end_year = Column(Integer, nullable=True)
    links = Column(JSON, nullable=True)
    priority = Column(Integer, nullable=True, default=0)
    profileId = Column(UUID, ForeignKey("Profile.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
