from app.db.db import Base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import timezone, datetime
import uuid
import enum


class RoleTypeEnum(str, enum.Enum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"


class LocationTypeEnum(str, enum.Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"


class JobDescription(Base):
    __tablename__ = "JobDescription"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    Role_Name = Column(String, nullable=True, index=True)
    Company = Column(String, nullable=True, index=True)
    Role_Type = Column(
        SQLEnum(RoleTypeEnum), nullable=True, default=RoleTypeEnum.FULL_TIME, index=True
    )
    Location = Column(
        SQLEnum(LocationTypeEnum),
        nullable=True,
        default=LocationTypeEnum.REMOTE,
        index=True,
    )
    Location_City = Column(String, nullable=True)
    Salary_Min = Column(String, nullable=True)
    Salary_Max = Column(String, nullable=True)
    Salary_Currency = Column(String, nullable=True)
    Duration = Column(String, nullable=True)
    Tech_Stack = Column(ARRAY(String), default=[])
    Required_Skills = Column(ARRAY(String), default=[])
    Experience_Required = Column(String, nullable=True)
    Summary = Column(String, nullable=True)
    Raw_JD = Column(String, nullable=False)
    Created_At = Column(DateTime, default=datetime.now(timezone.utc))
    Updated_At = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
