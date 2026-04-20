from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Project(Base):
    __tablename__ = "Profile"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    full_name = Column(String, nullable=False, unique=True, index=True)
    summary = Column(String, nullable=True)
    headline = Column(String, nullable=False)
    links = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
