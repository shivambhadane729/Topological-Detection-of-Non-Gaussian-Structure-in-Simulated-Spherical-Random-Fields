from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.configs import settings

# Import Routers
from backend.routers import upload, preprocess, compute, results

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for CosmoPH - Topological Detection of Non-Gaussianities",
    version="1.0.0"
)

# CORS Middleware (Allow frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["Upload"])
app.include_router(preprocess.router, prefix=f"{settings.API_V1_STR}/preprocess", tags=["Preprocessing"])
app.include_router(compute.router, prefix=f"{settings.API_V1_STR}/compute-tda", tags=["TDA Computation"])
app.include_router(results.router, prefix=f"{settings.API_V1_STR}/results", tags=["Results"])

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API. Please visit /docs for Swagger documentation."
    }