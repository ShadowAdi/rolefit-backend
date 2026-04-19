from fastapi import APIRouter
from app.api.v1.health import health_router

v1_router = APIRouter()

v1_router.include_router(health_router.router, prefix="/health", tags=["health"])
