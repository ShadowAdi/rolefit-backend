from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.User import User
from app.schema.auth import LoginRequest
from app.response.user_responses import UserAuthenticatedResponse
from app.core.logger import logger
from app.utils.utils import verify_password, create_access_token, TOKEN_EXPIRE
from app.validators.user_validators import UserValidator


class AuthServiceClass:
    def loginUser(self, db: Session, data: LoginRequest) -> UserAuthenticatedResponse:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            data: Login request with email and password

        Returns:
            UserAuthenticatedResponse with user details and access token

        Raises:
            HTTPException: For validation, authentication, or database errors
        """
        try:
            try:
                UserValidator.validate_email(data.email.lower().strip())
            except ValueError as e:
                logger.warning(f"Email validation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(e),
                )

            try:
                UserValidator.validate_password(data.password)
            except ValueError as e:
                logger.warning(f"Password validation failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(e),
                )

            existing_user = (
                db.query(User)
                .filter(func.lower(User.email) == data.email.lower().strip())
                .first()
            )
            if not existing_user:
                logger.warning(f"User with this email does not exist: {data.email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User with this email does not exist",
                )

            isPasswordCorrect = verify_password(data.password, existing_user.password)
            if not isPasswordCorrect:
                logger.warning(
                    f"Invalid password attempt for user: {existing_user.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                )

            access_token = create_access_token(
                user_id=str(existing_user.id), email=existing_user.email
            )

            response = UserAuthenticatedResponse(
                id=existing_user.id,
                email=existing_user.email,
                created_at=existing_user.created_at,
                access_token=access_token,
                token_type="bearer",
                expires_in=TOKEN_EXPIRE * 60,
            )

            logger.info(f"User {existing_user.email} logged in successfully")
            return response

        except HTTPException:
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during login: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Data conflict during authentication",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during login: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during authentication",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during authentication",
            )
