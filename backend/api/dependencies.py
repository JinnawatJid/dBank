from typing import Generator
from backend.db.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency function to yield a database session.
    Automatically closes the session when the request is finished.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
