from fastapi import APIRouter, HTTPException
from backend.models.schemas import TDARequest, TDAResponse
from backend.services.tda_service import TDAService

router = APIRouter()

@router.post("/", response_model=TDAResponse, summary="Compute Persistent Homology")
def compute_tda(request: TDARequest):
    \"\"\"
    Initiates TDA computation and Topology Feature Extraction asynchronously.
    \"\"\"
    try:
        job_id = TDAService.enqueue_tda_computation(request)
        return TDAResponse(
            job_id=job_id,
            status="queued",
            message="TDA computation job added to queue"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))