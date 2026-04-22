from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schema.auth import LoginRequest
from app.response.user_responses import UserAuthenticatedResponse
from .auth_service import AuthServiceClass
from app.dependency.dependencies import get_db
from app.core.logger import logger

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
    responses={
        422: {"description": "Validation Error"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)

auth_service = AuthServiceClass()


@router.post(
    "/login",
    response_model=UserAuthenticatedResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password",
)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> UserAuthenticatedResponse:
    """
    Login endpoint that authenticates a user.

    **Request Body:**
    - `email`: User's email address (must be valid email format)
    - `password`: User's password (minimum 6 characters)

    **Returns:**
    - User details with JWT access token
    - Token type: bearer
    - Token expiration time in seconds

    **Possible Errors:**
    - 422: Invalid email or password format
    - 401: Incorrect email or password
    - 404: User not found
    - 500: Server error
    """
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        response = auth_service.loginUser(db=db, data=login_data)
        return response
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}", exc_info=True)
        raise
