from app.db.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import timezone, datetime
import uuid


class JobDescription(Base):
    __tablename__ = "JobDescription"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    Company = Column(String, nullable=False, index=True)
    Role_Type = Column(String, nullable=False, default="Full-time", index=True)
    Location = Column(String, nullable=False, index=True, default="Remote")
    Location_City = Column(String, nullable=False)
    Salary_Min = Column(String, nullable=False)
    Salary_Max = Column(String, nullable=False)
    Salary_Currency = Column(String, nullable=False)
    Tech_Stack = Column(ARRAY(String), default=[])
    Required_Skills = Column(ARRAY(String), default=[])
    Experience_Required = Column(ARRAY(String))
    Summary = Column(String)
    Raw_JD = Column(String)
