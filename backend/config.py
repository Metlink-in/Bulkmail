from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "bulkreach_prod"
    JWT_SECRET_KEY: str = "fallback_secret_key_change_me_in_production_12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "vggzlymdyhsslvnx_vggzlymdyhsslvnx" # 32 bytes
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_NAME: str = "Admin User"
    APP_ENV: str = "production"
    BACKEND_URL: str = ""
    FRONTEND_URL: str = ""
    CORS_ORIGINS: str = "*"
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
