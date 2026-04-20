from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone, datetime
import uuid


class Profile(Base):
    __tablename__ = "Profile"
    __table_args__ = (UniqueConstraint("userId", name="uq_profile_user_id"),)

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False, unique=True)
    full_name = Column(String, nullable=False, index=True)
    summary = Column(String, nullable=True)
    headline = Column(String, nullable=False)
    links = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
