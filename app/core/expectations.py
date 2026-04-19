from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import logger
from app.core.AppError import AppError


async def app_error_handler(request: Request, exc: AppError):
    """Handle custom AppError exceptions"""
    logger.warning(
        f"AppError - Code: {exc.error_code}, Status: {exc.status_code}, Message: {exc.message}"
    )
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions from Starlette"""
    logger.warning(
        f"HTTP Exception - Status: {exc.status_code}, Detail: {exc.detail}, Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_code": "HTTP_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    errors = exc.errors()
    logger.warning(f"Validation Error - Count: {len(errors)}, Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": errors,
            "path": request.url.path,
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"Unhandled Exception - Type: {type(exc).__name__}, Message: {str(exc)}, Path: {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path,
        },
    )
