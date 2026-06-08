from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.db.db import get_db
from app.models.User import User
from app.models.UserVerification import EmailVerification
from app.schema.UserVerification import (
    EmailVerificationResponse,
    ResendVerificationRequest,
    EmailVerificationStatus,
)
from app.core.email import send_verification_email
from app.utils.generate_verification_token import generate_verification_token
from app.core.logger import logger

router = APIRouter(prefix="/verify", tags=["Email Verification"])


@router.get("/email", response_model=EmailVerificationResponse)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user's email address with the provided token.

    Args:
        token: Verification token sent to user's email
        db: Database session

    Returns:
        EmailVerificationResponse: Verification status
    """
    # Find valid verification record
    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.token == token,
            EmailVerification.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if not verification:
        logger.warning(f"Invalid or expired verification token used")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # Get the associated user
    user = db.query(User).filter(User.id == verification.user_id).first()

    if not user:
        logger.error(f"User not found for verification token: {token}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_verified:
        logger.info(f"User {user.email} already verified")
        return EmailVerificationResponse(
            message="Email already verified",
            is_verified=True,
            verified_at=user.updated_at,
        )

    # Mark user as verified
    user.is_verified = True
    user.updated_at = datetime.now(timezone.utc)

    # Optionally delete or keep the verification record
    # db.delete(verification)  # Uncomment if you want to delete after verification

    db.commit()

    logger.info(f"User {user.email} successfully verified")

    return EmailVerificationResponse(
        message="Email verified successfully! You can now log in.",
        is_verified=True,
        verified_at=user.updated_at,
    )


@router.post("/resend", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Resend verification email to user.

    Args:
        request: Contains user email
        background_tasks: FastAPI background tasks
        db: Database session
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()

    if not user:
        # Don't reveal that user doesn't exist for security reasons
        logger.info(
            f"Resend verification requested for non-existent email: {request.email}"
        )
        return {
            "message": "If your email is registered, you will receive a verification link"
        }

    if user.is_verified:
        logger.info(
            f"Verification resend requested for already verified user: {user.email}"
        )
        return {"message": "Email is already verified. Please log in."}

    # Generate new token
    new_token = generate_verification_token()
    token_expires = datetime.now(timezone.utc) + timedelta(hours=24)

    # Check if verification record exists
    verification = (
        db.query(EmailVerification).filter(EmailVerification.user_id == user.id).first()
    )

    if verification:
        # Update existing record
        verification.token = new_token
        verification.expires_at = token_expires
        verification.created_at = datetime.now(timezone.utc)
    else:
        # Create new record
        verification = EmailVerification(
            user_id=user.id, token=new_token, expires_at=token_expires
        )
        db.add(verification)

    db.commit()

    # Send verification email in background
    background_tasks.add_task(send_verification_email, user.email, new_token)

    logger.info(f"Verification email resent to {user.email}")

    return {"message": "Verification email sent. Please check your inbox."}


@router.get("/status", response_model=EmailVerificationStatus)
async def get_verification_status(email: str, db: Session = Depends(get_db)):
    """
    Check if a user's email is verified.

    Args:
        email: User email address
        db: Database session

    Returns:
        EmailVerificationStatus: Verification status
    """
    user = db.query(User).filter(User.email == email.lower().strip()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return EmailVerificationStatus(
        is_verified=user.is_verified, user_id=user.id, email=user.email
    )
