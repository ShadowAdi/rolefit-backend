"""
Pydantic schema for the cover letter JSON produced by the AI.
This is the contract between content_service (AI output) and build_pdf (PDF renderer).
"""

from pydantic import BaseModel, Field


class CandidateInfo(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str | None = None


class CompanyInfo(BaseModel):
    name: str = ""
    role: str = ""


class CoverLetterParagraphs(BaseModel):
    opening: str = ""
    body1: str = ""
    body2: str = ""
    closing: str = ""


class CoverLetterData(BaseModel):
    candidate: CandidateInfo
    company: CompanyInfo
    date: str = ""
    paragraphs: CoverLetterParagraphs
    sign_off: str = "Sincerely"
