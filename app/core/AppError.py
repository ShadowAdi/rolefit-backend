from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.core.logger import logger
from fastapi.responses import JSONResponse
from fastapi import Request
from pydantic import ValidationError


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for API responses"""
        return {
            "success": False,
            "error": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code,
            "timestamp": self.timestamp,
            "details": self.details,
        }


def app_error_handler(error: "AppError") -> JSONResponse:
    """Generic error handler for AppError"""
    logger.error(
        f"Application error: {error.message} (status: {error.status_code}, code: {error.error_code})"
    )
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict(),
    )


def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for FastAPI/Pydantic validation errors"""
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "status_code": 422,
            "details": exc.errors(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
