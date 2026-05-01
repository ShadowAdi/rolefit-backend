from app.db.redis_db import redis
from app.core.logger import logger


async def get_cache(key: str):
    if not redis:
        logger.warning("Redis not initialized. Cache retrieval skipped.")
        return None
    try:
        return await redis.get(key)
    except Exception as e:
        logger.error(f"Error retrieving cache for key {key}: {str(e)}")
        return None


async def set_cache(key: str, value: str, ttl: int = 300):
    if not redis:
        logger.warning("Redis not initialized. Cache write skipped.")
        return
    try:
        await redis.set(key, value, ex=ttl)
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {str(e)}")


async def delete_cache(key: str):
    if not redis:
        logger.warning("Redis not initialized. Cache deletion skipped.")
        return
    try:
        await redis.delete(key)
    except Exception as e:
        logger.error(f"Error deleting cache for key {key}: {str(e)}")


async def invalidate_user_cache(user_id: str):
    """
    Invalidate (delete) the authentication cache for a specific user.
    Call this when user profile is updated or deleted.

    Args:
        user_id: The ID of the user whose cache should be invalidated
    """
    try:
        cache_key = f"authenticated-user-{user_id}"
        await delete_cache(cache_key)
        logger.info(f"User cache invalidated: {user_id}")
    except Exception as e:
        logger.error(
            f"Error invalidating cache for user {user_id}: {str(e)}", exc_info=True
        )
        # Don't raise - cache invalidation failure shouldn't break the request
