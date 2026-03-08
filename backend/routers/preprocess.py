from fastapi import APIRouter

router = APIRouter(prefix="/preprocess", tags=["Preprocess"])

@router.post("/")
def preprocess_data():
    return {
        "status": "preprocessing started"
    }