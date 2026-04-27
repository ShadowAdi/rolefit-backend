from pydantic import BaseModel


class Counts(BaseModel):
    experience: int
    academics: int
    achievements: int
    projects: int
    publications: int
    skills: int
    tools: int


class ResumeExtractorResponse(BaseModel):
    profile_id: str
    counts: Counts
