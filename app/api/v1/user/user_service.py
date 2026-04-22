from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from app.models.User import User
from app.schema.User import UserCreateRequest, UserResponse
from app.core.logger import logger
from app.utils.utils import hash_password
from app.validators.user_validators import UserValidator


class UserServiceClass:
    """Service class for user-related operations"""

    def register(self, db: Session, data: UserCreateRequest) -> UserResponse:
        """
        Register a new user with validation and error handling.

        Args:
            db: Database session
            data: User registration data

        Returns:
            UserResponse: Created user data

        Raises:
            HTTPException: For validation or database errors
        """
        try:
            try:
                validated_email = UserValidator.validate_email(data.email)
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

            existing_user = db.query(User).filter(User.email == data.email).first()
            if existing_user:
                logger.warning(
                    f"Registration attempted with existing email: {data.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

            user = User(
                email=validated_email,
                password=hash_password(data.password),
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"User successfully registered: {user.email}")
            return UserResponse.model_validate(user)

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during user registration: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during user registration: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during registration",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during user registration: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during registration",
            )

    def get_current_user(self, db: Session, user_id: str) -> UserResponse:
        """
        Retrieve current user profile by user ID.

        Args:
            db: Database session
            user_id: User unique identifier (UUID format)

        Returns:
            UserResponse: User profile data

        Raises:
            HTTPException: If user not found or database error
        """
        try:
            if not user_id:
                logger.warning("Get current user attempted with empty user_id")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User ID cannot be empty",
                )

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Current user not found: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.info(f"Current user profile retrieved successfully: {user.email}")
            return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error retrieving current user: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving current user: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )

    def delete_user(self, db: Session, user_id: str) -> UUID:
        """
        Delete a user account permanently.

        Args:
            db: Database session
            user_id: User unique identifier (UUID format)

        Returns:
            UUID: ID of the deleted user

        Raises:
            HTTPException: If user not found, validation fails, or database error
        """
        try:
            if not user_id:
                logger.warning("Delete user attempted with empty user_id")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User ID cannot be empty",
                )

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"Delete attempted on non-existent user: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            deleted_user_id = user.id

            db.delete(user)
            db.commit()

            logger.info(f"User successfully deleted: {user.email}")
            return deleted_user_id

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during user delete: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Failed to delete user due to data constraints",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting user: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred during delete",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error deleting user: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during delete",
            )


UserService = UserServiceClass()
