#!/usr/bin/env python
"""
Debug script to check Celery task queuing and execution
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.celery_app import celery_app
from app.core.logger import logger
import redis
from dotenv import load_dotenv

load_dotenv()


def check_redis_connection():
    """Check if Redis is accessible"""
    try:
        redis_url = os.getenv("REDIS_CELERY_URL", "redis://localhost:6379/0")
        print(f"Redis URL: {redis_url}")

        # Parse Redis URL
        if redis_url.startswith("redis://"):
            # Simple parsing for redis://host:port/db format
            parts = redis_url.replace("redis://", "").split("/")
            host_port = parts[0]
            db = parts[1] if len(parts) > 1 else "0"

            host, port = host_port.split(":")
            port = int(port)
            db = int(db)

            print(f"Connecting to Redis: host={host}, port={port}, db={db}")
            r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            r.ping()
            print("✓ Redis connection successful!")
            return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False


def check_celery_config():
    """Check Celery configuration"""
    print("\nCelery Configuration:")
    print(f"Broker: {celery_app.conf.broker_url}")
    print(f"Backend: {celery_app.conf.result_backend}")
    print(f"Task Serializer: {celery_app.conf.task_serializer}")
    print(f"Result Serializer: {celery_app.conf.result_serializer}")


def check_registered_tasks():
    """Check registered tasks"""
    print("\nRegistered Celery Tasks:")
    for task_name in celery_app.tasks:
        if not task_name.startswith("celery"):
            print(f"  ✓ {task_name}")


def test_queue_task():
    """Test queueing a task"""
    try:
        print("\nTesting task queue...")

        # Try to queue a simple test
        from app.tasks.ai_tasks import cleanup_old_tasks

        task = cleanup_old_tasks.delay()
        print(f"✓ Task queued successfully!")
        print(f"  Task ID: {task.id}")
        print(f"  Task State: {task.state}")

        return True
    except Exception as e:
        print(f"✗ Task queue failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CELERY DEBUG DIAGNOSTICS")
    print("=" * 60)

    check_redis_connection()
    check_celery_config()
    check_registered_tasks()
    test_queue_task()
