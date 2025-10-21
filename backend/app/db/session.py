from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI or "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
