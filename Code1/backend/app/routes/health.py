"""CosmoPH - Health Check Route"""
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()

@router.get("/health")
async def health_check():
    s = get_settings()
    return {
        "status": "healthy",
        "app": s.APP_NAME,
        "version": s.APP_VERSION,
        "debug": s.DEBUG,
    }
