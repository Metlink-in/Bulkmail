from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BulkReach Pro"
    MONGODB_URI: str
    JWT_SECRET: str
    JWT_ADMIN_SECRET: str
    FERNET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
