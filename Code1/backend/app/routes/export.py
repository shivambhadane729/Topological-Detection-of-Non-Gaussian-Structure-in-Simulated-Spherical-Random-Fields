"""CosmoPH - Export Route"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.job_manager import get_job
from app.services.export_service import create_zip_bundle
from app.config import get_settings

router = APIRouter()

@router.get("/export/{job_id}")
async def export_results(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(400, "Job not yet completed")
    result = job.get("result", {})
    if not result:
        raise HTTPException(400, "No results to export")
    zip_path = create_zip_bundle(job_id, result)
    return FileResponse(zip_path, media_type="application/zip",
                        filename=f"cosmoph_results_{job_id}.zip")

@router.get("/export/{job_id}/json")
async def export_json(job_id: str):
    job = get_job(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(404, "Completed job not found")
    return job.get("result", {})
