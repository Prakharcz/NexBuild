import logging
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.config import settings
from app.db.seed import seed_demo_data
from app.models.user import User

# Ensure all models are loaded
import app.models  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Ensure all SQL database tables exist.
    If SEED_DEMO_DATA is enabled and no user exists, load the realistic demo dataset.
    """
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    if settings.SEED_DEMO_DATA:
        with SessionLocal() as db:
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("Database is empty. Populating demo financial dataset...")
                try:
                    seed_demo_data(db)
                except Exception as e:
                    logger.error(f"Failed to auto-seed demo data: {e}")
            else:
                logger.info("Database already contains users. Skipping auto-seeding.")


if __name__ == "__main__":
    init_db()
