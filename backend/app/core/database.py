from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError
import os
import time
import logging

# Enhanced database configuration with connection pooling
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:hive123@hive_postgres:5432/hive")

# Create engine with connection pooling and reliability features
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragma for foreign key support"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def get_db():
    """Database session dependency with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except DisconnectionError as e:
        logging.error(f"Database disconnection error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logging.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_database_connection():
    """Test database connectivity"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

def init_database_with_retry(max_retries=5, retry_delay=2):
    """Initialize database with retry logic"""
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logging.info("Database initialized successfully")
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Database initialization failed after {max_retries} attempts: {e}")
                raise
            logging.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
            time.sleep(retry_delay ** attempt)
    return False