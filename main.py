from fastapi import FastAPI
from sqlalchemy import text
import feedparser
import requests
import os
import json
from dotenv import load_dotenv

from app.db import db as database
from app.core.logger import logger
from app.core.AppError import AppError, app_error_handler
from contextlib import asynccontextmanager
from app.core.cors import setup_cors

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application - initializing database...")
    await database.init_db()
    logger.info("Database initialized successfully")

    yield

    logger.info("Shutting down application...")
    if database.engine:
        database.engine.dispose()


app = FastAPI(lifespan=lifespan)

setup_cors(app=app)
app.add_exception_handler(AppError, app_error_handler)


@app.get("/")
def read_root():
    return {"Hello": "World"}
