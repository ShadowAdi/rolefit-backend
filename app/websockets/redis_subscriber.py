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
                    logger.info(
                        f"[Redis subscriber] Received event: type={event.get('type')} doc_id={event.get('doc_id')} user_id={event.get('user_id')}"
                    )
                except json.JSONDecodeError:
                    logger.warning(
                        f"[Redis subscriber] Bad JSON: {message['data'][:100]}"
                    )
                    continue

                user_id = event.get("user_id")
                if not user_id:
                    logger.warning("[Redis subscriber] Event missing user_id — skipped")
                    continue

                logger.info(f"[Redis subscriber] Sending event to user_id={user_id}")
                await manager.send(user_id, event)

        except asyncio.CancelledError:
            logger.info("[Redis subscriber] Cancelled — shutting down")
            break
        except Exception as e:
            logger.error(f"[Redis subscriber] Error: {e} — reconnecting in 3s")
            await asyncio.sleep(3)


def publish_event_sync(redis_url: str, event: dict):
    """
    Synchronous function to publish events to Redis.
    Called from Celery tasks (which run in separate threads).
    """
    try:
        r = sync_redis.from_url(redis_url, decode_responses=True)
        payload = json.dumps(event)
        result = r.publish(CHANNEL, payload)
        r.close()
        logger.info(
            f"[Redis publish] Event sent to {result} subscriber(s): doc_id={event.get('doc_id')} user_id={event.get('user_id')}"
        )
    except Exception as e:
        logger.error(f"[Redis publish] Failed to publish event: {e}", exc_info=True)
