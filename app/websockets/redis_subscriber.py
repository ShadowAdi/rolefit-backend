import json
import asyncio
import logging
import os

import redis.asyncio as aioredis
from app.websockets.connection_manager import manager
import redis as sync_redis

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CHANNEL = "rolefit:events"


async def start_redis_subscriber():
    logger.info(f"[Redis subscriber] Starting on channel={CHANNEL}")

    while True:
        try:
            redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
            pubsub = redis.pubsub()
            await pubsub.subscribe(CHANNEL)
            logger.info(f"[Redis subscriber] Subscribed to {CHANNEL}")

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                try:
                    event = json.loads(message["data"])
                except json.JSONDecodeError:
                    logger.warning(
                        f"[Redis subscriber] Bad JSON: {message['data'][:100]}"
                    )
                    continue

                user_id = event.get("user_id")
                if not user_id:
                    logger.warning("[Redis subscriber] Event missing user_id — skipped")
                    continue

                await message.send(user_id, event)

        except asyncio.CancelledError:
            logger.info("[Redis subscriber] Cancelled — shutting down")
            break
        except Exception as e:
            logger.error(f"[Redis subscriber] Error: {e} — reconnecting in 3s")
            await asyncio.sleep(3)


async def publish_event_sync(redis_url: str, event: dict):
    r = sync_redis.from_url(redis_url, decode_responses=True)
    r.publish(CHANNEL, json.dumps(event))
    r.close()
