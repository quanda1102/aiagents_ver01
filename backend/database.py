from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()