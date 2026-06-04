from app.db import redis_db
from app.core.logger import logger


async def get_cache(key: str):
    if not redis_db.redis:
        logger.warning("Redis not initialized. Cache retrieval skipped.")
        return None
    try:
        return await redis_db.redis.get(key)
    except Exception as e:
        logger.error(f"Error retrieving cache for key {key}: {str(e)}")
        return None


async def set_cache(key: str, value: str, ttl: int = 300):
    if not redis_db.redis:
        logger.warning("Redis not initialized. Cache write skipped.")
        return
    try:
        await redis_db.redis.set(key, value, ex=ttl)
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {str(e)}")


async def delete_cache(key: str):
    if not redis_db.redis:
        logger.warning("Redis not initialized. Cache deletion skipped.")
        return
    try:
        await redis_db.redis.delete(key)
    except Exception as e:
        logger.error(f"Error deleting cache for key {key}: {str(e)}")


async def invalidate_user_profile_cache(user_id: str):
    """
    Invalidate (delete) the cached profile for a specific user.

    This is the cache populated by `get_user_profile` (key
    `authenticated-profile-{user_id}`) and read by the experience, academics,
    publications and achievement services. It MUST be cleared whenever the
    user's profile is created, replaced or deleted, otherwise those services
    keep resolving a stale (often deleted) profile id and return empty lists
    even though the data exists under the new profile.

    Args:
        user_id: The ID of the user whose profile cache should be invalidated
    """
    try:
        cache_key = f"authenticated-profile-{user_id}"
        await delete_cache(cache_key)
        logger.info(f"User profile cache invalidated: {user_id}")
    except Exception as e:
        logger.error(
            f"Error invalidating profile cache for user {user_id}: {str(e)}",
            exc_info=True,
        )
        # Don't raise - cache invalidation failure shouldn't break the request


async def invalidate_user_cache(user_id: str):
    """
    Invalidate (delete) the authentication and profile caches for a user.
    Call this when the user profile is created, updated or deleted.

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

    # Also clear the cached profile so profile-scoped services (experience,
    # academics, publications, achievements) don't resolve a stale profile id.
    await invalidate_user_profile_cache(user_id)
