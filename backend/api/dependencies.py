from typing import Generator
from backend.db.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency function to yield a database session.
    Automatically closes the session when the request is finished,
    and rolls back any pending transactions if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
