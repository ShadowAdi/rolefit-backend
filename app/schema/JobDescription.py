from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime


class RoleTypeEnum(str, Enum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"


class JDInput(BaseModel):
    payload: str


class LocationTypeEnum(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"


class JobDescriptionCreate(BaseModel):
    """Schema for creating a new job description"""

    model_config = ConfigDict(populate_by_name=True)

    user_id: Optional[str] = Field(None)  # UUID as string; typically from auth context
    role_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    role_type: Optional[RoleTypeEnum] = None
    location: Optional[LocationTypeEnum] = None
    location_city: Optional[str] = Field(None, max_length=255)
    salary_min: Optional[str] = Field(None, max_length=255)
    salary_max: Optional[str] = Field(None, max_length=255)
    salary_currency: Optional[str] = Field(None, max_length=10)
    duration: Optional[str] = Field(None, max_length=255)
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    required_skills: Optional[List[str]] = Field(default_factory=list)
    experience_required: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    raw_jd: str = Field(..., min_length=1)
    company_name: Optional[str] = None
    company_information: Optional[str] = Field(None, min_length=1, max_length=1000)
    company_website_url: Optional[str] = None


class JobDescriptionUpdate(BaseModel):
    """Schema for updating a job description"""

    model_config = ConfigDict(populate_by_name=True)
    role_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    role_type: Optional[RoleTypeEnum] = None
    location: Optional[LocationTypeEnum] = None
    location_city: Optional[str] = Field(None, max_length=255)
    salary_min: Optional[str] = Field(None, max_length=255)
    salary_max: Optional[str] = Field(None, max_length=255)
    salary_currency: Optional[str] = Field(None, max_length=10)
    duration: Optional[str] = Field(None, max_length=255)
    tech_stack: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=2000)
    raw_jd: Optional[str] = Field(None, min_length=1)
    company_name: Optional[str] = None
    company_information: Optional[str] = Field(None, min_length=1, max_length=1000)
    company_website_url: Optional[str] = None


class JobDescriptionResponse(BaseModel):
    """Schema for job description response"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    role_name: Optional[str]
    company: Optional[str]
    role_type: Optional[str]
    location: Optional[str]
    location_city: Optional[str]
    salary_min: Optional[str]
    salary_max: Optional[str]
    salary_currency: Optional[str]
    duration: Optional[str]
    tech_stack: List[str]
    required_skills: List[str]
    experience_required: Optional[str]
    summary: Optional[str]
    raw_jd: str
    company_name: Optional[str]
    company_information: Optional[str]
    company_website_url: Optional[str]
    created_at: datetime
    updated_at: datetime
