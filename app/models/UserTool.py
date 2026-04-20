from app.db.db import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserTool(Base):
    __tablename__ = "UserTool"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    userId = Column(UUID, ForeignKey("User.id"), nullable=False)
    toolId = Column(UUID, ForeignKey("Tool.id"), nullable=False)
