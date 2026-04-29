from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "bulkreach_prod"
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = ""
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "Admin"
    APP_ENV: str = "production"
    BACKEND_URL: str = ""
    FRONTEND_URL: str = ""
    CORS_ORIGINS: str = "*"
    GEMINI_API_KEY: Optional[str] = None

    # Default SMTP loaded from .env (applied to admin account on demand)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = False
    SMTP_USE_SSL: bool = False
    SMTP_FROM_NAME: Optional[str] = None
    SMTP_REPLY_TO: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
