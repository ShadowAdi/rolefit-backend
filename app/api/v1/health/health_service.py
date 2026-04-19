from fastapi import status
from app.core.AppError import AppError


class HealthService:
    def get_health(self):
        return {"status": "ok", "message": "API is working"}


health_service = HealthService()
