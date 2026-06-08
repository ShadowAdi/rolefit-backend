from fastapi import APIRouter
from app.api.v1.health import health_router
from app.api.v1.user import user_router
from app.api.v1.auth import auth_router
from app.api.v1.profile import profile_router
from app.api.v1.project import project_router
from app.api.v1.experience import experience_router
from app.api.v1.publications import publication_router
from app.api.v1.academics import academics_router
from app.api.v1.skill import skill_router
from app.api.v1.tools import tool_router
from app.api.v1.job_description import jd_router
from app.api.v1.content import content_router
from app.api.v1.resume import resume_router
from app.api.v1.cover_letter import cover_letter_router
from app.api.v1.resume_extractor import resume_extractor_router
from app.api.v1.websocket import websocket_router
from app.api.v1.apiKeys import apiKeys_router
from app.api.v1.dashboard import dashboard_router
from app.api.v1.verification import verification_router

v1_router = APIRouter()

v1_router.include_router(health_router.router, prefix="/health")
v1_router.include_router(user_router.router, prefix="/user")
v1_router.include_router(auth_router.router, prefix="/auth")
v1_router.include_router(profile_router.router, prefix="/profile")
v1_router.include_router(project_router.router, prefix="/project")
v1_router.include_router(experience_router.router, prefix="/experience")
v1_router.include_router(academics_router.router, prefix="/academics")
v1_router.include_router(publication_router.router, prefix="/publications")
v1_router.include_router(skill_router.router, prefix="/skills")
v1_router.include_router(tool_router.router, prefix="/tools")
v1_router.include_router(jd_router.router, prefix="/job-descriptions")
v1_router.include_router(content_router.router, prefix="/content")
v1_router.include_router(resume_router.router, prefix="/resume")
v1_router.include_router(cover_letter_router.router, prefix="/cover-router")
v1_router.include_router(resume_extractor_router.router, prefix="/resume-extractor")
v1_router.include_router(websocket_router.router, prefix="/websocket")
v1_router.include_router(dashboard_router.router, prefix="/dashboard")
v1_router.include_router(apiKeys_router.router, prefix="/api-keys")
v1_router.include_router(verification_router, prefix="/verification")
