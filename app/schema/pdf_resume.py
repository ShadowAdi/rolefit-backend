"""
Pydantic schema for the resume JSON produced by the AI.
This is the contract between content_service (AI output) and build_pdf (PDF renderer).
"""

from pydantic import BaseModel


class Header(BaseModel):
    name: str
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[str] = []


class SkillGroup(BaseModel):
    category: str
    items: list[str]


class Experience(BaseModel):
    role: str
    company: str
    location: str = ""
    start: str = ""
    end: str = ""
    bullets: list[str] = []


class Project(BaseModel):
    title: str
    tech: str = ""
    bullets: list[str] = []
    links: list[str] = []


class Publication(BaseModel):
    title: str
    publisher: str = ""
    year: str = ""


class Education(BaseModel):
    degree: str
    institution: str
    location: str = ""
    year: str = ""
    description: str = ""


class ResumeData(BaseModel):
    header: Header
    summary: str | None = None
    skills: list[SkillGroup] = []
    experience: list[Experience] = []
    projects: list[Project] = []
    achievements: list[str] = []
    publications: list[Publication] = []
    education: list[Education] = []
