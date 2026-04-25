from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import threading

# Configuration for Database (Switched to SQLite for easy local testing)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./retail_analytics.db")

Base = declarative_base()

class DatabaseSessionManager:
    """
    Singleton Pattern Implementation for PostgreSQL database connection pool.
    This ensures that multiple API requests don't spawn redundant database engines.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseSessionManager, cls).__new__(cls)
                cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, db_url: str = DATABASE_URL):
        # SQLite needs check_same_thread=False for FastAPI dependency injection
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

        # Pool-size arguments are not supported by SQLite's StaticPool
        engine_kwargs: dict = dict(connect_args=connect_args)
        if not db_url.startswith("sqlite"):
            engine_kwargs.update(
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
            )

        self.engine = create_engine(db_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        """
        Dependency injection method for FastAPI to yield session.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Initialize the Singleton manager
db_manager = DatabaseSessionManager()

def get_db():
    return db_manager.get_session()
