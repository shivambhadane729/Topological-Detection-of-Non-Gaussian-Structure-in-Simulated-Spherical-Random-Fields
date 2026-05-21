"""
CosmoPH - Data Loader Service
Handles loading FITS files, sample datasets, and managing the dataset registry.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Optional
from app.config import get_settings

# Try importing healpy - fall back to numpy-based demo if not available
try:
    import healpy as hp
    HEALPY_AVAILABLE = True
except ImportError:
    HEALPY_AVAILABLE = False
    print("⚠️  healpy not available. Using synthetic data mode.")

try:
    from astropy.io import fits as astropy_fits
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False
    print("⚠️  astropy not available. Using basic FITS loading.")


# ── Dataset Registry ─────────────────────────────────────────────────
# This registry maps dataset IDs to their metadata and file locations.

DATASET_REGISTRY = {
    "planck_commander_full": {
        "id": "planck_commander_full",
        "name": "Planck Commander CMB Map (Full Sky)",
        "filename": "COM_CMB_IQU-commander_2048_R3.00_full.fits",
        "category": "raw",
        "description": "Full-sky CMB temperature map from Planck 2018 Commander component separation. NSIDE=2048.",
        "nside": 2048,
        "source_url": "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-commander_2048_R3.00_full.fits",
    },
    "planck_mask": {
        "id": "planck_mask",
        "name": "Planck Common Mask",
        "filename": "COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.00.fits",
        "category": "raw",
        "description": "Common analysis mask for Planck CMB maps. Masks galactic plane and point sources.",
        "nside": 2048,
        "source_url": "https://irsa.ipac.caltech.edu/data/Planck/release_2/ancillary-data/masks/COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.00.fits",
    },
    "demo_gaussian_64": {
        "id": "demo_gaussian_64",
        "name": "Gaussian Random Field (NSIDE=64)",
        "filename": "gaussian_sample_nside64.npy",
        "category": "sample",
        "description": "Synthetic Gaussian random field at NSIDE=64. Used as null comparison for non-Gaussianity detection.",
        "nside": 64,
        "source_url": None,
    },
    "demo_cmb_patch": {
        "id": "demo_cmb_patch",
        "name": "Demo CMB Patch (64x64)",
        "filename": "demo_cmb_patch_64x64.npy",
        "category": "sample",
        "description": "Pre-generated 64x64 pixel CMB patch for quick demo and testing. Contains subtle non-Gaussian features.",
        "nside": None,
        "source_url": None,
    },
    "demo_non_gaussian": {
        "id": "demo_non_gaussian",
        "name": "Non-Gaussian Demo Patch",
        "filename": "demo_non_gaussian_patch_64x64.npy",
        "category": "sample",
        "description": "Synthetic patch with injected non-Gaussian features (chi-squared perturbations) for demonstration.",
        "nside": None,
        "source_url": None,
    },
}


def get_dataset_registry() -> dict:
    """Return dataset registry with availability status."""
    settings = get_settings()
    registry = {}
    
    for ds_id, ds_info in DATASET_REGISTRY.items():
        info = ds_info.copy()
        
        # Determine folder based on category
        if ds_info["category"] == "raw":
            folder = settings.RAW_DIR
        elif ds_info["category"] == "sample":
            folder = settings.SAMPLE_DIR
        elif ds_info["category"] == "processed":
            folder = settings.PROCESSED_DIR
        else:
            folder = settings.DATASET_DIR / ds_info["category"]
        
        filepath = folder / ds_info["filename"]
        info["is_available"] = filepath.exists()
        info["filepath"] = str(filepath)
        
        if filepath.exists():
            info["file_size_mb"] = round(filepath.stat().st_size / (1024 * 1024), 2)
        else:
            info["file_size_mb"] = None
        
        registry[ds_id] = info
    
    return registry


def load_fits_map(filepath: str, field: int = 0) -> np.ndarray:
    """
    Load a HEALPix FITS map from disk.
    
    Args:
        filepath: Path to the FITS file
        field: Field index to read (0 for temperature)
    
    Returns:
        numpy array of pixel values
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"FITS file not found: {filepath}")
    
    if HEALPY_AVAILABLE:
        try:
            data = hp.read_map(str(filepath), field=field, dtype=np.float64)
            # Replace UNSEEN values with NaN
            data[data == hp.UNSEEN] = np.nan
            return data
        except Exception as e:
            raise ValueError(f"Error loading FITS with healpy: {e}")
    elif ASTROPY_AVAILABLE:
        try:
            with astropy_fits.open(str(filepath)) as hdul:
                data = hdul[1].data.field(field).astype(np.float64)
                return data
        except Exception as e:
            raise ValueError(f"Error loading FITS with astropy: {e}")
    else:
        raise ImportError("Neither healpy nor astropy available. Cannot load FITS files.")


def load_numpy_data(filepath: str) -> np.ndarray:
    """Load a numpy .npy or .npz file."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    if filepath.suffix == ".npy":
        return np.load(str(filepath))
    elif filepath.suffix == ".npz":
        data = np.load(str(filepath))
        return data[list(data.keys())[0]]
    else:
        raise ValueError(f"Unsupported file type: {filepath.suffix}")


def load_dataset(dataset_id: str) -> np.ndarray:
    """
    Load a dataset by its registry ID.
    
    Args:
        dataset_id: ID from the dataset registry
    
    Returns:
        numpy array of the loaded data
    """
    registry = get_dataset_registry()
    
    if dataset_id not in registry:
        raise ValueError(f"Unknown dataset: {dataset_id}")
    
    info = registry[dataset_id]
    filepath = info["filepath"]
    
    if not info["is_available"]:
        raise FileNotFoundError(
            f"Dataset '{info['name']}' is not available on disk. "
            f"Expected path: {filepath}"
        )
    
    if filepath.endswith((".fits", ".fit", ".fts")):
        return load_fits_map(filepath)
    elif filepath.endswith((".npy", ".npz")):
        return load_numpy_data(filepath)
    else:
        raise ValueError(f"Unsupported file format for dataset: {filepath}")


def load_uploaded_file(filepath: str) -> np.ndarray:
    """
    Load a user-uploaded file.
    
    Args:
        filepath: Path to the uploaded file
    
    Returns:
        numpy array of the loaded data
    """
    filepath = Path(filepath)
    
    if filepath.suffix in (".fits", ".fit", ".fts"):
        return load_fits_map(str(filepath))
    elif filepath.suffix in (".npy", ".npz"):
        return load_numpy_data(str(filepath))
    else:
        raise ValueError(f"Unsupported file type: {filepath.suffix}")


def generate_demo_data():
    """
    Generate all demo/sample datasets if they don't exist.
    Called during application startup.
    """
    settings = get_settings()
    settings.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Gaussian random field (flat patch)
    gaussian_path = settings.SAMPLE_DIR / "gaussian_sample_nside64.npy"
    if not gaussian_path.exists():
        np.random.seed(42)
        gaussian_map = np.random.normal(0, 1e-5, (64, 64))
        np.save(str(gaussian_path), gaussian_map)
        print(f"✅ Generated: {gaussian_path}")
    
    # 2. Demo CMB patch (Gaussian + small signal)
    demo_path = settings.SAMPLE_DIR / "demo_cmb_patch_64x64.npy"
    if not demo_path.exists():
        np.random.seed(123)
        # Simulate a CMB-like patch with power spectrum-like correlations
        x = np.linspace(-3, 3, 64)
        y = np.linspace(-3, 3, 64)
        X, Y = np.meshgrid(x, y)
        
        # Gaussian random field with spatial correlations
        from scipy.ndimage import gaussian_filter
        raw = np.random.normal(0, 1, (64, 64))
        cmb_patch = gaussian_filter(raw, sigma=2.0) * 1e-5
        
        np.save(str(demo_path), cmb_patch)
        print(f"✅ Generated: {demo_path}")
    
    # 3. Non-Gaussian demo patch (for comparison)
    ng_path = settings.SAMPLE_DIR / "demo_non_gaussian_patch_64x64.npy"
    if not ng_path.exists():
        np.random.seed(456)
        from scipy.ndimage import gaussian_filter
        raw = np.random.normal(0, 1, (64, 64))
        gaussian_part = gaussian_filter(raw, sigma=2.0) * 1e-5
        
        # Add non-Gaussian perturbation (chi-squared like)
        chi2_perturbation = (np.random.normal(0, 1, (64, 64))**2 - 1) * 3e-6
        ng_patch = gaussian_part + chi2_perturbation
        
        # Add some local extrema (hot/cold spots)
        ng_patch[20:25, 30:35] += 5e-5
        ng_patch[40:45, 10:15] -= 4e-5
        
        np.save(str(ng_path), ng_patch)
        print(f"✅ Generated: {ng_path}")
    
    return True

