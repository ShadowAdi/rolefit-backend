from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Academic(Base):
    __tablename__ = "Academic"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    degree_name = Column(String, nullable=False, index=True)
    college_name = Column(String, nullable=False, index=True)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    description = Column(String, nullable=True)
    links = Column(JSON, nullable=True)
    start_month = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
