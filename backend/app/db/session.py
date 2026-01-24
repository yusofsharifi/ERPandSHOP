from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI or "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Optional read-replica engine
READ_REPLICA_URL = settings.READ_REPLICA_DATABASE_URI
read_replica_engine = None
if READ_REPLICA_URL:
    try:
        read_replica_engine = create_engine(READ_REPLICA_URL, connect_args={"check_same_thread": False} if READ_REPLICA_URL.startswith("sqlite") else {})
    except Exception:
        read_replica_engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Helper to get engine (use read-replica for heavy reads if available)
def get_engine(prefer_read: bool = False):
    if prefer_read and read_replica_engine is not None:
        return read_replica_engine
    return engine
