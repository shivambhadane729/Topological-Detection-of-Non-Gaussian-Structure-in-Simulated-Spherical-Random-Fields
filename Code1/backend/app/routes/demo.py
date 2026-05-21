"""CosmoPH - Demo Route
One-click demo: generates sample data, preprocesses, runs TDA, returns results.
"""
import numpy as np
from fastapi import APIRouter
from app.services.data_loader import generate_demo_data
from app.services.preprocessor import preprocess_pipeline
from app.services.tda_engine import run_tda_pipeline
from app.services.ml_classifier import classify_inflation_model
from app.services.gaussian_generator import generate_gaussian_field, generate_non_gaussian_field
from app.services.job_manager import create_job, update_job
from app.schemas.job import JobStatus
import time

router = APIRouter()

@router.post("/demo")
async def run_demo(patch_size: int = 64, f_nl: float = 100.0):
    """Run complete demo pipeline with synthetic data."""
    jid = create_job("demo", {"patch_size": patch_size, "f_nl": f_nl})
    update_job(jid, status=JobStatus.RUNNING, message="Generating demo data...")
    try:
        # Generate non-Gaussian patch
        ng_patch = generate_non_gaussian_field(
            shape=(patch_size, patch_size), f_nl=f_nl, seed=42
        )
        # Preprocess
        prep = preprocess_pipeline(ng_patch, apply_mask=False, patch_size=patch_size, normalize=True)
        patch = prep["patch"]
        # TDA
        tda = run_tda_pipeline(patch, max_points=800, n_gaussian_samples=3)
        # Classify
        tda["classification"] = classify_inflation_model(tda)
        tda["preprocessing"] = prep["stats"]
        tda["demo_params"] = {"patch_size": patch_size, "f_nl": f_nl}
        update_job(jid, status=JobStatus.COMPLETED, result=tda,
                   progress=100.0, message="Demo completed",
                   completed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        return {"job_id": jid, "status": "completed", "result": tda}
    except Exception as e:
        update_job(jid, status=JobStatus.FAILED, error=str(e))
        return {"job_id": jid, "status": "failed", "error": str(e)}

@router.get("/demo/sample-data")
async def get_sample_data():
    """Return sample datasets info for demo."""
    generate_demo_data()
    from app.services.data_loader import get_dataset_registry
    reg = get_dataset_registry()
    samples = {k: v for k, v in reg.items() if v["category"] == "sample"}
    return {"samples": samples, "total": len(samples)}
