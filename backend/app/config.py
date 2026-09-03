"""
Application configuration.

Loads settings from environment variables / .env file using pydantic-settings.
Keep secrets (DB credentials, JWT secret, AWS keys, OpenAI key) out of source
control — they should already be sitting in backend/.env (git-ignored).
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "Kiwi-Biz Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Database ---
    # e.g. postgresql://user:password@localhost:5432/kiwibiz
    DATABASE_URL: str

    # --- JWT Auth ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- AWS S3 ---
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str | None = None

    # --- Document storage backend ---
    # Switch between "local" and "s3" by changing this one line.
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    # Where uploaded files live when STORAGE_BACKEND = "local".
    # Relative to backend/ (the directory you run uvicorn from).
    LOCAL_STORAGE_DIR: str = "storage/uploads"

    # --- OpenAI ---
    OPENAI_API_KEY: str | None = None

    # --- CORS ---
    # Comma-separated origins in .env, e.g. "http://localhost:5173,http://localhost:3000"
   #CORS_ORIGINS: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — avoids re-parsing .env on every import."""
    return Settings()


settings = get_settings()
