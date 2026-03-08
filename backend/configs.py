import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CosmoPH"
    API_V1_STR: str = "/api/v1"
    
    # Celery & Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # Storage layer configuration
    STORAGE_DIR: str = os.path.join(os.path.dirname(__file__), "storage")
    CMB_FILE_STORAGE: str = os.path.join(STORAGE_DIR, "cmb_maps")
    TOPOLOGY_RESULT_STORAGE: str = os.path.join(STORAGE_DIR, "results")
    
    # Limits
    MAX_UPLOAD_SIZE_MB: int = 500
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.CMB_FILE_STORAGE, exist_ok=True)
os.makedirs(settings.TOPOLOGY_RESULT_STORAGE, exist_ok=True)
