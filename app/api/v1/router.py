from fastapi import APIRouter
from app.api.v1.health import health_router
from app.api.v1.user import user_router
from app.api.v1.auth import auth_router
from app.api.v1.profile import profile_router
from app.api.v1.project import project_router


v1_router = APIRouter()

v1_router.include_router(health_router.router, prefix="/health", tags=["health"])
v1_router.include_router(user_router.router, prefix="/user", tags=["user"])
v1_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
v1_router.include_router(profile_router.router, prefix="/profile", tags=["profile"])
v1_router.include_router(project_router.router, prefix="/project", tags=["project"])
