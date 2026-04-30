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
