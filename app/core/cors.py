import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger


def setup_cors(app: FastAPI):
    ENV = os.getenv("ENV", "development")

    if ENV == "development":
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    else:
        PROD_URL = os.getenv("PROD_URL")

        origins = [PROD_URL]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["Content-Length", "Authorization"],
    )

    logger.info(f"CORS configured for: {origins}")
