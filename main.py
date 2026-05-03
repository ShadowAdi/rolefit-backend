from fastapi import FastAPI
from dotenv import load_dotenv

from app.db import db as database
from app.db import redis_db as redis_database
from app.core.logger import logger
from app.core.AppError import AppError, app_error_handler
from contextlib import asynccontextmanager
from app.core.cors import setup_cors
from app.api.router import api_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application - initializing database...")
    await database.init_db()
    try:
        await redis_database.init_redis()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}", exc_info=True)
    logger.info("Database initialized successfully")

    yield

    logger.info("Shutting down application...")
    if database.engine:
        database.engine.dispose()
    await redis_database.close_redis()


app = FastAPI(lifespan=lifespan)

setup_cors(app=app)
app.add_exception_handler(AppError, app_error_handler)
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}
