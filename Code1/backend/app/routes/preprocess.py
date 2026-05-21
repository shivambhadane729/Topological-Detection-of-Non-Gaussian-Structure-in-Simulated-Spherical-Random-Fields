"""CosmoPH - Preprocess Route"""
import numpy as np
from fastapi import APIRouter, HTTPException
from app.schemas.preprocess import PreprocessConfig
from app.services.data_loader import load_dataset, load_uploaded_file, get_dataset_registry
from app.services.preprocessor import preprocess_pipeline
from app.services.job_manager import create_job, run_job_async, get_job
from app.config import get_settings

router = APIRouter()

def _run_preprocess(config: dict):
    reg = get_dataset_registry()
    ds_id = config["dataset_id"]
    if ds_id not in reg:
        raise ValueError(f"Dataset not found: {ds_id}")
    info = reg[ds_id]
    # Load data
    if info["category"] == "uploaded":
        s = get_settings()
        data = load_uploaded_file(str(s.UPLOAD_DIR / info["filename"]))
    else:
        data = load_dataset(ds_id)
    # Note: data can be 1D (HEALPix) or 2D (patch). 
    # The `preprocess_pipeline` -> `extract_patch` function will safely handle it.
    result = preprocess_pipeline(
        data,
        apply_mask=config.get("apply_mask", True),
        patch_size=config.get("patch_size", 64),
        patch_center_lon=config.get("patch_center_lon", 0.0),
        patch_center_lat=config.get("patch_center_lat", 90.0),
        normalize=config.get("normalize", True),
        apply_filter=config.get("apply_filter", False),
        filter_scale=config.get("filter_scale", 1.0),
    )
    # Save patch for next step
    s = get_settings()
    patch_path = s.PROCESSED_DIR / f"patch_{config['job_id']}.npy"
    np.save(str(patch_path), result["patch"])
    return {
        "patch_shape": list(result["patch"].shape),
        "pixel_stats": result["stats"],
        "mask_applied": result["mask_applied"],
        "filter_applied": result["filter_applied"],
        "preview_data": result["patch"].tolist(),
        "message": "Preprocessing completed",
    }

@router.post("/preprocess")
async def preprocess(config: PreprocessConfig):
    jid = create_job("preprocess", config.model_dump())
    cfg = config.model_dump()
    cfg["job_id"] = jid
    run_job_async(jid, _run_preprocess, cfg)
    return {"job_id": jid, "status": "pending", "message": "Preprocessing started"}

@router.get("/preprocess/{job_id}")
async def get_preprocess_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job
