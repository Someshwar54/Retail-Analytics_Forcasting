from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from ..db.session import db_manager

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to yield a database session from the Singleton pool.
    """
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()
