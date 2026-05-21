"""CosmoPH - Results Route"""
import json
from fastapi import APIRouter, HTTPException
from app.services.job_manager import get_job, list_jobs
from app.services.ml_classifier import classify_inflation_model
from app.config import get_settings

router = APIRouter()

@router.get("/results/{job_id}")
async def get_results(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        return {"job_id": job_id, "status": job["status"], "message": job.get("message", "")}
    result = job.get("result", {})
    # Add ML classification if TDA results available
    if result and "persistence_diagram" in result:
        result["classification"] = classify_inflation_model(result)
    return {"job_id": job_id, "status": "completed", "result": result}

@router.get("/results")
async def list_all_results():
    jobs = list_jobs()
    return {"jobs": jobs, "total": len(jobs)}
