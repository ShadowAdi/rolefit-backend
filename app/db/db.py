import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import logger
from app.core.AppError import AppError

DATABASE_URL = os.getenv("DATABASE_URL")


def _pg_connect_args(database_url: str) -> dict:
    """
    Build psycopg2 connect args, deciding the SSL mode.

    Managed Postgres (Neon, Render, Supabase, ...) *requires* TLS, while a
    local Docker Postgres typically has TLS off. Precedence:
      1. If the URL already pins `sslmode=...`, respect it (and don't pass a
         conflicting kwarg to the driver).
      2. Otherwise fall back to the DB_SSLMODE env var, defaulting to
         `require` so cloud deployments work out of the box.
    Set DB_SSLMODE=disable (or put ?sslmode=disable in the URL) for local dev.
    """
    if "postgresql" not in database_url.lower():
        return {}
    if "sslmode=" in database_url.lower():
        return {}
    return {"sslmode": os.getenv("DB_SSLMODE", "require")}


if not DATABASE_URL:
    logger.exception("DATABASE_URL environment variable is not set")
    raise AppError(
        message="Database configuration is missing",
        status_code=500,
        error_code="DB_CONFIG_ERROR",
        details={"issue": "DATABASE_URL environment variable not found"},
    )


async def connect_with_retry(
    database_url: str, max_retries: int = 5, initial_delay: float = 2
):
    """
    Async database connection with exponential backoff.
    """
    retry_count = 0
    delay = initial_delay

    connect_args = _pg_connect_args(database_url)

    while retry_count < max_retries:
        try:
            logger.info(
                f"Attempting to connect to database (attempt {retry_count + 1}/{max_retries})..."
            )

            engine = create_engine(
                url=database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                connect_args=connect_args,
            )

            # Test connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            logger.info("Database connection successful")
            return engine

        except SQLAlchemyError as e:
            retry_count += 1
            logger.warning(
                f"DB connection failed (attempt {retry_count}/{max_retries}): {type(e).__name__}"
            )

            if retry_count >= max_retries:
                logger.exception("Max retries reached. Could not connect to database.")
                raise AppError(
                    message="Failed to connect to database after multiple attempts",
                    status_code=500,
                    error_code="DB_CONNECTION_ERROR",
                ) from e

            await asyncio.sleep(delay)
            delay *= 2  # exponential backoff

        except Exception as e:
            retry_count += 1
            logger.warning(f"Unexpected error during connection: {type(e).__name__}")

            if retry_count >= max_retries:
                logger.exception("Max retries reached with unexpected error.")
                raise AppError(
                    message="Unexpected error connecting to database",
                    status_code=500,
                    error_code="DB_UNEXPECTED_ERROR",
                    details={"error": str(e)},
                ) from e

            await asyncio.sleep(delay)
            delay *= 2


engine = None
SessionLocal = None
Base = declarative_base()


def init_db_sync():
    """Initialize database synchronously for Celery workers"""
    global engine, SessionLocal

    if engine is not None:
        return  # Already initialized

    try:
        logger.info("Initializing database for Celery worker...")

        connect_args = _pg_connect_args(DATABASE_URL)

        engine = create_engine(
            url=DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            connect_args=connect_args,
        )

        # Test connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connection successful (sync)")

        # Create all tables
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )
        logger.info("Database initialized successfully (sync)")

    except Exception as e:
        logger.error(f"Failed to initialize database (sync): {str(e)}", exc_info=True)
        raise


async def init_db():
    """Initialize database with async retry"""
    global engine, SessionLocal

    engine = await connect_with_retry(DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    except Exception:
        logger.exception("Unexpected database session error")
        db.rollback()
        raise
    finally:
        db.close()
