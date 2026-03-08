from fastapi import APIRouter

router = APIRouter(prefix="/compute-tda", tags=["Compute"])

@router.post("/")
def compute_tda():
    return {"status": "TDA computation started"}