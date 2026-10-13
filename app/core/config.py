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

    DEMO_MODE_ENABLED: bool = True

    DOCUMENT_WORKER_ENABLED: bool = True

    
settings = Settings()