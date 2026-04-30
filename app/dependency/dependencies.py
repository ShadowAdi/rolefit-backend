from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.utils import decode_token
from app.db.db import get_db
from app.models.User import User
from app.core.logger import logger
from app.helpers.redis_cache_helpers import set_cache, get_cache, delete_cache
from fastapi.encoders import jsonable_encoder
import json

bearer = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT token.

    Args:
        creds: HTTP Bearer credentials containing JWT token
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If token is invalid, expired, or user doesn't exist
    """
    try:
        if not creds or not creds.credentials:
            logger.warning("Authentication attempted without token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token provided",
            )

        token = creds.credentials

        payload = decode_token(token=token)
        if not payload:
            logger.warning("Invalid or expired token attempted")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing user ID claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Check Redis cache first
        cache_key = f"authenticated-user-{user_id}"
        cached_user = await get_cache(cache_key)
        if cached_user:
            logger.debug(f"User retrieved from cache: {user_id}")
            user_data = json.loads(cached_user)
            # Reconstruct User object from cached data
            user = User(**user_data)
            return user

        # If not in cache, query database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User from token no longer exists: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )

        # Cache the user for 15 minutes (900 seconds)
        user_data = jsonable_encoder(user)
        await set_cache(cache_key, json.dumps(user_data), 900)

        logger.info(f"User authenticated successfully: {user.email}")
        return user

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during authentication",
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication",
        )
