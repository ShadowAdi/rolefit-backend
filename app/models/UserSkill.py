from app.db.db import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserSkill(Base):
    __tablename__ = "UserSkill"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    skillId = Column(UUID, ForeignKey("Skill.id"), nullable=False)
