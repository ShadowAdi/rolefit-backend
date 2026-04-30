from app.db.redis_db import redis
from app.core.logger import logger


async def get_cache(key: str):
    if not redis:
        logger.error("Redis not initialized. Call init_redis() first.")
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return await redis.get(key)


async def set_cache(key: str, value: str, ttl: int = 300):
    if not redis:
        logger.error("Redis not initialized. Call init_redis() first.")
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    await redis.set(key, value, ex=ttl)


async def delete_cache(key: str):
    if not redis:
        logger.error("Redis not initialized. Call init_redis() first.")
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    await redis.delete(key)


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
