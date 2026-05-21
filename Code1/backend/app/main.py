"""
CosmoPH - Main FastAPI Application
Entry point for the backend server with all route registrations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings, ensure_directories
from app.routes import health, datasets, upload, preprocess, compute, results, export, demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    ensure_directories()
    print("🚀 CosmoPH backend is starting up...")
    yield
    print("🛑 CosmoPH backend is shutting down...")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "CosmoPH: A web-based platform for Topological Data Analysis (TDA) "
        "on Cosmic Microwave Background (CMB) maps to detect primordial non-Gaussianity."
    ),
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for exports
app.mount("/static/outputs", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="outputs")

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(datasets.router, prefix="/api", tags=["Datasets"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(preprocess.router, prefix="/api", tags=["Preprocessing"])
app.include_router(compute.router, prefix="/api", tags=["TDA Compute"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(demo.router, prefix="/api", tags=["Demo"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
