import json
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import make_transient
from sqlalchemy.exc import SQLAlchemyError
from app.utils.utils import decode_token
from app.db.db import get_db
from app.models.User import User
from app.core.logger import logger
from app.helpers.redis_cache_helpers import set_cache, get_cache

bearer = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)
) -> User:
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

        cache_key = f"authenticated-user-{user_id}"
        cached_user = await get_cache(cache_key)

        if cached_user:
            logger.debug(f"User retrieved from cache: {user_id}")
            user_data = json.loads(cached_user)

            user = User(
                id=uuid.UUID(str(user_data["id"])),
                email=user_data["email"],
            )
            make_transient(user)
            return user

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User from token no longer exists: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )

        cached_data = {
            "id": str(user.id),
            "email": user.email,
        }
        await set_cache(cache_key, json.dumps(cached_data), 900)
        logger.debug(f"User cached: {user_id}")

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
