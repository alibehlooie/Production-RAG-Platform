from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    APP_NAME: str = "Local AI RAG Platform"
    DATABASE_URL: str

    DEMO_MODE_ENABLED: bool = True
    JWT_SECRET_KEY: str = "local-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_STORAGE_PATH: Path = Path("storage/uploads")
    UPLOAD_MAX_BYTES: int = 20 * 1024 * 1024  # 20 MB

    DOCUMENT_WORKER_ENABLED: bool = True
    DOCUMENT_WORKER_POLL_SECONDS: float = 2.0
    DOCUMENT_WORKER_STALE_AFTER_SECONDS: int = 300

    EMBEDDING_BASE_URL: str = "http://localhost:1234/v1"
    EMBEDDING_API_KEY: str = "lm-studio"
    EMBEDDING_MODEL: str = "text-embedding-nomic-embed-text-v1.5"
    EMBEDDING_DIMENSIONS: int = 768


settings = Settings()