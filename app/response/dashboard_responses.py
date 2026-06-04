from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class DashboardStats(BaseModel):
    """High level counters for the authenticated user."""

    totalJobDescriptions: int = Field(..., description="Number of job descriptions saved")
    totalDocuments: int = Field(..., description="Total generated documents")
    totalResumes: int = Field(..., description="Generated resumes")
    totalCoverLetters: int = Field(..., description="Generated cover letters")
    completedDocuments: int = Field(..., description="Documents with completed status")
    pendingDocuments: int = Field(
        ..., description="Documents that are pending or processing"
    )
    failedDocuments: int = Field(..., description="Documents that failed to generate")


class ProfileSummary(BaseModel):
    """Snapshot of the user's profile completeness."""

    fullName: Optional[str] = Field(None, description="User's full name")
    headline: Optional[str] = Field(None, description="Profile headline")
    isOnboarded: bool = Field(False, description="Whether onboarding is complete")
    totalProjects: int = Field(0, description="Number of projects")
    totalExperiences: int = Field(0, description="Number of experiences")
    totalSkills: int = Field(0, description="Number of skills")
    totalTools: int = Field(0, description="Number of tools")
    totalPublications: int = Field(0, description="Number of publications")
    totalAcademics: int = Field(0, description="Number of academic records")


class RecentJob(BaseModel):
    """A recently added job description."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Job description id")
    roleName: Optional[str] = Field(None, description="Role name")
    company: Optional[str] = Field(None, description="Company name")
    roleType: Optional[str] = Field(None, description="Role type")
    location: Optional[str] = Field(None, description="Location type")
    createdAt: Optional[datetime] = Field(None, description="Creation timestamp")


class RecentDocument(BaseModel):
    """A recently generated document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Document id")
    type: str = Field(..., description="Document type (Resume / Cover-letter)")
    status: str = Field(..., description="Generation status")
    createdAt: Optional[datetime] = Field(None, description="Creation timestamp")


class DashboardResponse(BaseModel):
    """Aggregated dashboard payload."""

    stats: DashboardStats
    profile: ProfileSummary
    recentJobs: List[RecentJob]
    recentDocuments: List[RecentDocument]
