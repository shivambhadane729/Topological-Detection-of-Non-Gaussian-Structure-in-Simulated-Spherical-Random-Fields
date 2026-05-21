"""CosmoPH - FITS Utilities"""
import numpy as np
from pathlib import Path

def validate_fits_file(filepath: str) -> dict:
    """Validate a FITS file and return basic info."""
    p = Path(filepath)
    if not p.exists():
        return {"valid": False, "error": "File not found"}
    if p.suffix.lower() not in ('.fits', '.fit', '.fts'):
        return {"valid": False, "error": f"Not a FITS file: {p.suffix}"}
    if p.stat().st_size < 2880:  # Min FITS size
        return {"valid": False, "error": "File too small to be valid FITS"}
    # Check magic bytes
    with open(p, 'rb') as f:
        header = f.read(8)
        if not header.startswith(b'SIMPLE'):
            return {"valid": False, "error": "Invalid FITS header"}
    return {"valid": True, "size_mb": round(p.stat().st_size / 1048576, 2), "filename": p.name}

def get_fits_info(filepath: str) -> dict:
    """Get metadata from a FITS file."""
    try:
        from astropy.io import fits
        with fits.open(filepath) as hdul:
            info = {"n_extensions": len(hdul), "extensions": []}
            for i, hdu in enumerate(hdul):
                ext = {"index": i, "name": hdu.name, "type": type(hdu).__name__}
                if hdu.data is not None:
                    ext["shape"] = list(hdu.data.shape)
                    ext["dtype"] = str(hdu.data.dtype)
                info["extensions"].append(ext)
            return info
    except ImportError:
        return {"note": "astropy not available for detailed FITS inspection"}
    except Exception as e:
        return {"error": str(e)}
