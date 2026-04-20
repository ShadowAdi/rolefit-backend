from fastapi import APIRouter, Depends, status
from app.schema.Profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .profile_service import ProfileServiceClass
from datetime import datetime, timezone
from app.models.User import User
from app.dependency.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(data: ProfileCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        data: User registration data (email, password, username, profile_url, bio)
        db: Database session

    Returns:
        RegisterApiResponse: User account created with success status
    """
    profile = ProfileServiceClass.create_profile(db=db, data=data)

    return ProfileResponse(
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="Profile registered successfully",
        data=ProfileResponse.model_validate(profile),
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(
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
    profile = ProfileServiceClass.get_profile(db, current_user.id)

    return ProfileResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Profile fetched successfully",
        data=profile,
        timestamp=datetime.now(timezone.utc),
    )


@router.delete(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
def delete_profile(
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
    profile = ProfileServiceClass.delete_profile(db, current_user.id)

    return ProfileResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Profile deleted successfully",
        data=profile,
        timestamp=datetime.now(timezone.utc),
    )
