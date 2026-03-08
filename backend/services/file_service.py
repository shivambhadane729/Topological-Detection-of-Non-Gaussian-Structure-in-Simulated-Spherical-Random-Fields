import os
import shutil
import uuid
from fastapi import UploadFile
from backend.configs import settings

class FileService:
    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> str:
        \"\"\"
        Saves a CMB FITS map to the configured storage and returns a unique map_id.
        \"\"\"
        map_id = str(uuid.uuid4())
        # Safe ext check, assume .fits 
        ext = ".fits" if upload_file.filename.endswith(".fits") else ""
        file_name = f"{map_id}{ext}"
        file_path = os.path.join(settings.CMB_FILE_STORAGE, file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return map_id

    @staticmethod
    def get_file_path(map_id: str, ext: str = ".fits") -> str:
        \"\"\"
        Returns the absolute file path for a stored CMB map.
        \"\"\"
        file_name = f"{map_id}{ext}"
        file_path = os.path.join(settings.CMB_FILE_STORAGE, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Map with ID {map_id} not found.")
        return file_path
