from app.core.redis_keys import REDIS_URL
from redis.asyncio import Redis

redis: Redis | None = None


async def init_redis():
    global redis
    redis = Redis.from_url(REDIS_URL, decode_responses=True)


async def close_redis():
    global redis
    if redis:
        await redis.close()
