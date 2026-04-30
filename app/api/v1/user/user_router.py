from fastapi import APIRouter, Depends, status
from app.schema.User import (
    RegisterApiResponse,
    UserRegisterResponse,
    GetUserApiResponse,
    DeleteUserApiResponse,
    UserDeleteResponse,
)
from app.schema.User import UserCreateRequest, UserUpdateRequest, UserResponse
from sqlalchemy.orm import Session
from app.db.db import get_db
from .user_service import UserService
from datetime import datetime, timezone
from app.models.User import User
from app.dependency.dependencies import get_current_user

router = APIRouter(tags=["Users"])


@router.post(
    "/register",
    response_model=RegisterApiResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        data: User registration data (email, password, username, profile_url, bio)
        db: Database session

    Returns:
        RegisterApiResponse: User account created with success status
    """
    user = UserService.register(db=db, data=data)

    return RegisterApiResponse(
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=UserRegisterResponse.model_validate(user),
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/me",
    response_model=GetUserApiResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        GetUserApiResponse: Current user profile data
    """
    user = UserService.get_current_user(db, current_user.id)

    return GetUserApiResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="User profile fetched successfully",
        data=user,
        timestamp=datetime.now(timezone.utc),
    )


@router.delete(
    "/me",
    response_model=DeleteUserApiResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete current authenticated user profile permanently.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        DeleteUserApiResponse: Deletion confirmation with deleted user ID

    Raises:
        HTTPException: If validation fails or deletion fails
    """
    deleted_user_id = UserService.delete_user(db=db, user_id=str(current_user.id))

    return DeleteUserApiResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="User profile deleted successfully",
        data=UserDeleteResponse(
            success=True,
            message="User account deleted successfully",
            deleted_user_id=deleted_user_id,
            deleted_at=datetime.now(timezone.utc),
        ),
        timestamp=datetime.now(timezone.utc),
    )
