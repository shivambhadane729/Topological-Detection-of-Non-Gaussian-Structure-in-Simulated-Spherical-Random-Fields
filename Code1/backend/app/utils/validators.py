"""CosmoPH - Input Validators"""
from pathlib import Path
from app.config import get_settings

ALLOWED = {'.fits', '.fit', '.fts', '.npy', '.npz'}

def validate_upload(filename: str, size_bytes: int) -> dict:
    s = get_settings()
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED:
        return {"valid": False, "error": f"File type {ext} not allowed. Allowed: {ALLOWED}"}
    max_bytes = s.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return {"valid": False, "error": f"File too large ({size_bytes/1048576:.1f}MB). Max: {s.MAX_UPLOAD_SIZE_MB}MB"}
    return {"valid": True}

def validate_patch_size(size: int) -> bool:
    return 8 <= size <= 512

def validate_nside(nside: int) -> bool:
    import math
    return nside > 0 and (nside & (nside - 1)) == 0 and nside <= 2048
