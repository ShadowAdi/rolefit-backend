from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Experience(Base):
    __tablename__ = "Experience"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    company_name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    techStack = Column(JSON, nullable=True)
    role = Column(String, nullable=False, index=True)
    employment_type = Column(String, nullable=True)
    location_type = Column(String, nullable=True)
    location_details = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    start_month = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_date = Column(DateTime, nullable=True)
    end_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True, default=0)
    profileId = Column(UUID, ForeignKey("Profile.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
