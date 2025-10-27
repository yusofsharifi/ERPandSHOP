from typing import List, Optional, Any, Dict
from pydantic import validator, EmailStr, BaseSettings
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "TOP WorX"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI backend
        "http://127.0.0.1:3000",  # React frontend local
        "http://185.92.183.137:3000",  # React frontend server
        "http://185.92.183.137:8000",  # FastAPI backend server
    ]
    # Database
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    SERVER_HOST: str = "http://localhost:8000"
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None
    # Read-replica (optional)
    READ_REPLICA_DATABASE_URI: Optional[str] = None
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    # OpenAI (for chatbot)
    OPENAI_API_KEY: Optional[str] = None
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.example.com"
    SMTP_USER: str = "user@example.com"
    SMTP_PASSWORD: str = "password"
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    # Internationalization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "fa"]

    @validator("EMAILS_FROM_NAME", pre=True, always=True)
    def get_emails_from_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        return v or values.get("PROJECT_NAME")

    @validator("EMAILS_FROM_EMAIL", pre=True, always=True)
    def get_emails_from_email(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        return v or values.get("SMTP_USER")

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "topworx"
    CACHE_TTL_SECONDS: int = 60

    @validator("SQLALCHEMY_DATABASE_URI", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v != "":
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
