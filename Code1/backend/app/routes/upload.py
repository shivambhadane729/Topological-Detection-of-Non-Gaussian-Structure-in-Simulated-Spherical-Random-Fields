"""CosmoPH - Upload Route"""
import shutil, uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import get_settings
from app.utils.validators import validate_upload
from app.services.data_loader import DATASET_REGISTRY

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    s = get_settings()
    s.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Read to check size
    contents = await file.read()
    size = len(contents)
    val = validate_upload(file.filename, size)
    if not val["valid"]:
        raise HTTPException(400, val["error"])
    # Save
    uid = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix
    save_name = f"upload_{uid}{ext}"
    save_path = s.UPLOAD_DIR / save_name
    with open(save_path, "wb") as f:
        f.write(contents)
    # Register as dataset
    ds_id = f"upload_{uid}"
    DATASET_REGISTRY[ds_id] = {
        "id": ds_id, "name": f"Uploaded: {file.filename}",
        "filename": save_name, "category": "uploaded",
        "description": f"User upload: {file.filename} ({size/1048576:.2f} MB)",
        "nside": None, "source_url": None,
    }
    return {
        "dataset_id": ds_id, "filename": save_name,
        "size_mb": round(size / 1048576, 2),
        "message": "File uploaded successfully",
    }
