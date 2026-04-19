from typing import Optional,Dict,Any
from datetime import datetime, timezone
from app.core.logger import logger
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(
        self,
        message:str,
        status_code:int=400,
        error_code:str="APP_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
            self.message=message
            self.status_code=status_code
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
            "timestamp": self.timestamp,
            "details": self.details
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