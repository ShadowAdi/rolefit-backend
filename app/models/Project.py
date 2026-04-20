from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Project(Base):
    __tablename__ = "Project"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=False)
    profileId = Column(UUID, ForeignKey("Profile.id"), nullable=False)
    techStack = Column(JSON, nullable=True)
    links = Column(JSON, nullable=True)
    startDate = Column(DateTime, nullable=True)
    endDate = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
