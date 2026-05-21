"""CosmoPH - TDA Compute Route"""
import numpy as np
from fastapi import APIRouter, HTTPException
from app.schemas.tda import TDAConfig
from app.services.tda_engine import run_tda_pipeline
from app.services.job_manager import create_job, run_job_async, get_job
from app.config import get_settings

router = APIRouter()

def _run_tda(config: dict):
    s = get_settings()
    patch_path = s.PROCESSED_DIR / f"patch_{config['job_id']}.npy"
    if not patch_path.exists():
        raise FileNotFoundError(f"Preprocessed patch not found for job {config['job_id']}")
    patch = np.load(str(patch_path))
    results = run_tda_pipeline(
        patch,
        max_dimension=config.get("max_dimension", 1),
        max_edge_length=config.get("max_edge_length", 2.0),
        max_points=config.get("max_points", 1000),
        compute_betti=config.get("compute_betti", True),
        compute_pi=config.get("compute_persistence_image", True),
        compare_gaussian=config.get("compare_gaussian", True),
        n_gaussian_samples=config.get("n_gaussian_samples", 5),
    )
    # Save results
    import json
    from app.utils.helpers import safe_json
    res_path = s.OUTPUT_DIR / f"tda_{config['tda_job_id']}.json"
    with open(str(res_path), 'w') as f:
        json.dump(safe_json(results), f)
    return results

@router.post("/compute-tda")
async def compute_tda(config: TDAConfig):
    tda_jid = create_job("tda", config.model_dump())
    cfg = config.model_dump()
    cfg["tda_job_id"] = tda_jid
    run_job_async(tda_jid, _run_tda, cfg)
    return {"job_id": tda_jid, "status": "pending", "message": "TDA computation started"}

@router.get("/compute-tda/{job_id}")
async def get_tda_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job
