from fastapi import APIRouter, HTTPException
from backend.models.schemas import JobStatusResponse, TDAResultData
from backend.services.result_service import ResultService

router = APIRouter()

@router.get("/job/{job_id}", response_model=JobStatusResponse, summary="Get Job Status")
def get_job_status(job_id: str):
    \"\"\"
    Checks the status of a background job (preprocessing or TDA).
    \"\"\"
    try:
        return ResultService.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map/{map_id}", response_model=TDAResultData, summary="Get TDA Results")
def get_tda_results(map_id: str):
    \"\"\"
    Retrieves the completed TDA results and classifications for a specific map.
    \"\"\"
    try:
        return ResultService.get_topology_result(map_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))