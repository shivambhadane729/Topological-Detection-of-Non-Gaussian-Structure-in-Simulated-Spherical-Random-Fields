from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.file_service import FileService

router = APIRouter()

@router.post("/", summary="Upload CMB Map")
async def upload_cmb_map(file: UploadFile = File(...)):
    \"\"\"
    Uploads a CMB map in FITS format.
    \"\"\"
    if not file.filename.endswith(".fits"):
        raise HTTPException(status_code=400, detail="Only .fits files are supported")
        
    try:
        map_id = await FileService.save_upload_file(file)
        return {"map_id": map_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")