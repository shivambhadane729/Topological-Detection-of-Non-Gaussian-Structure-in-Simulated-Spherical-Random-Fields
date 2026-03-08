from fastapi import APIRouter, HTTPException
from backend.models.schemas import PreprocessRequest, PreprocessResponse
from backend.services.preprocessing_service import PreprocessingService

router = APIRouter()

@router.post("/", response_model=PreprocessResponse, summary="Preprocess Map")
def preprocess_map(request: PreprocessRequest):
    \"\"\"
    Applies masking and filtering to a previously uploaded map asynchronously.
    \"\"\"
    try:
        job_id = PreprocessingService.enqueue_preprocessing(request)
        return PreprocessResponse(
            job_id=job_id,
            status="queued",
            message="Preprocessing job added to queue"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))