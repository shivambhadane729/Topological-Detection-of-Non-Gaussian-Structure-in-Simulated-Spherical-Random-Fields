"""
CosmoPH - Configuration Management
Centralized settings using pydantic-settings for environment variable management.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "CosmoPH"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_EXTENSIONS: list[str] = [".fits", ".fit", ".fts", ".npy", ".npz"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATASET_DIR: Path = BASE_DIR / "dataset"
    RAW_DIR: Path = DATASET_DIR / "raw"
    SAMPLE_DIR: Path = DATASET_DIR / "sample"
    PROCESSED_DIR: Path = DATASET_DIR / "processed"
    OUTPUT_DIR: Path = DATASET_DIR / "outputs"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # TDA Defaults
    TDA_MAX_DIMENSION: int = 1
    TDA_MAX_EDGE_LENGTH: float = 2.0
    TDA_MAX_POINTS: int = 1000
    PATCH_SIZE: int = 64
    DEFAULT_NSIDE: int = 64
    
    # Job settings
    JOB_TIMEOUT_SECONDS: int = 600
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


def ensure_directories():
    """Create all required directories if they don't exist."""
    settings = get_settings()
    for dir_path in [
        settings.DATASET_DIR,
        settings.RAW_DIR,
        settings.SAMPLE_DIR,
        settings.PROCESSED_DIR,
        settings.OUTPUT_DIR,
        settings.UPLOAD_DIR,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
