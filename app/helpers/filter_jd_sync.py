import asyncio
from app.core.logger import logger
from .filter_jd import filter_jd


def filter_jd_sync(job_id: str, user_id: str, db, content_type: str) -> dict:
    try:
        return asyncio.run(
            filter_jd(jobId=job_id, userId=user_id, db=db, content_type=content_type)
        )
    except Exception as e:
        logger.error(f"filter_jd_sync failed job={job_id} user={user_id}: {e}")
        raise
