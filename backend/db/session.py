from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings

# Create the SQLAlchemy engine using the read-only application user credentials
engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,        # Default pool size
    max_overflow=20      # Max additional connections to create
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
