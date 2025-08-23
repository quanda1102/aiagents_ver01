from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
import logging

logger = logging.getLogger(__name__)

# Create engine with custom pool settings
engine = create_engine(
    config.DATABASE_URL,
    pool_size=5,  # Set pool size to 5
    max_overflow=0,  # No additional connections allowed
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=True# Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_pool_status():
    """Get current pool status for monitoring"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow()
    }

def log_pool_status():
    """Log current pool status"""
    status = get_pool_status()
    logger.info(f"Database Pool Status: {status}")
    return status