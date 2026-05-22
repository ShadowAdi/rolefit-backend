"""One-off migration: add Profile.isOnboarded column.

Background:
    The app uses ``Base.metadata.create_all`` which only creates missing tables.
    It will NOT add new columns to tables that already exist, so the new
    ``isOnboarded`` column on ``Profile`` has to be added manually on databases
    that already had a ``Profile`` table before this change.

Run:
    python -m app.db.migrations.add_is_onboarded_to_profile

The migration is idempotent (safe to run more than once).
"""

from sqlalchemy import text
from app.db.db import DATABASE_URL, init_db_sync
from app.core.logger import logger


COLUMN_EXISTS_SQL = """
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'Profile' AND column_name = 'isOnboarded'
"""

ADD_COLUMN_SQL = """
ALTER TABLE "Profile"
ADD COLUMN "isOnboarded" BOOLEAN NOT NULL DEFAULT FALSE
"""

# Existing users that already have onboarding data should be considered onboarded.
BACKFILL_SQL = """
UPDATE "Profile" p
SET "isOnboarded" = TRUE
WHERE p."isOnboarded" = FALSE
  AND (
    EXISTS (SELECT 1 FROM "Experience" e WHERE e."profileId" = p.id)
    OR EXISTS (SELECT 1 FROM "Academic" a WHERE a."profileId" = p.id)
    OR EXISTS (SELECT 1 FROM "Project" pr WHERE pr."profileId" = p.id)
    OR EXISTS (SELECT 1 FROM "Publication" pu WHERE pu."profileId" = p.id)
    OR EXISTS (SELECT 1 FROM "UserSkill" us WHERE us."userId" = p."userId")
    OR EXISTS (SELECT 1 FROM "UserTool" ut WHERE ut."userId" = p."userId")
  )
"""


def run() -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    init_db_sync()
    from app.db.db import engine

    if engine is None:
        raise RuntimeError("Database engine failed to initialize")

    with engine.begin() as conn:
        existing = conn.execute(text(COLUMN_EXISTS_SQL)).fetchone()
        if existing:
            logger.info("Profile.isOnboarded column already exists — skipping ADD.")
        else:
            logger.info("Adding Profile.isOnboarded column...")
            conn.execute(text(ADD_COLUMN_SQL))
            logger.info("Column added.")

        logger.info("Backfilling isOnboarded for profiles with existing data...")
        result = conn.execute(text(BACKFILL_SQL))
        logger.info(
            f"Backfill complete. Rows updated: {result.rowcount}"
        )


if __name__ == "__main__":
    run()
