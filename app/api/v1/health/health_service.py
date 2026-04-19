from fastapi import status
from app.core.AppError import AppError


class HealthService:
    def get_health(self):
        return {"status": "ok", "message": "API is working", "success": True}


health_service = HealthService()
