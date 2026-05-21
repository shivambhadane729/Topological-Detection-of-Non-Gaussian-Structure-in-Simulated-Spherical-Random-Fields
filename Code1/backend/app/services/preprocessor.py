"""
CosmoPH - Preprocessor Service
Handles CMB map preprocessing: masking, patch extraction, normalization, and filtering.
"""

import numpy as np
from typing import Optional, Tuple
from app.config import get_settings

try:
    from scipy.ndimage import gaussian_filter
    from scipy.signal import cwt, ricker
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import healpy as hp
    HEALPY_AVAILABLE = True
except ImportError:
    HEALPY_AVAILABLE = False


def apply_map_mask(data: np.ndarray, mask: Optional[np.ndarray] = None, mask_type: str = "galactic") -> np.ndarray:
    """
    Apply galactic plane mask to a CMB map.
    
    If healpy is available and data is a 1D HEALPix map, applies the provided mask
    or generates a simple galactic plane mask.
    If data is a 2D patch, applies a simple border mask.
    
    Args:
        data: Input map data (1D HEALPix or 2D patch)
        mask: Optional binary mask (1=keep, 0=mask)
    
    Returns:
        Masked data with NaN in masked regions
    """
    result = data.copy().astype(np.float64)
    
    if mask is not None:
        if mask.shape == data.shape:
            result[mask == 0] = np.nan
        else:
            # Resize mask to match data
            if data.ndim == 2 and mask.ndim == 2:
                from scipy.ndimage import zoom
                zoom_factor = (data.shape[0] / mask.shape[0], data.shape[1] / mask.shape[1])
                resized_mask = zoom(mask.astype(float), zoom_factor, order=0)
                result[resized_mask < 0.5] = np.nan
    else:
        # Apply a simple synthetic mask for 2D patches based on mask_type
        if data.ndim == 2:
            h, w = data.shape
            if mask_type == "galactic":
                center = h // 2
                mask_width = max(1, h // 10)  # Mask 10% around center horizontal band
                result[center - mask_width:center + mask_width, :] = np.nan
            elif mask_type == "point_source":
                # Apply randomly scattered circular holes (like point sources)
                np.random.seed(42)  # Fixed seed for reproducibility so the mask is stable
                n_sources = max(3, (h * w) // 200)
                for _ in range(n_sources):
                    cy, cx = np.random.randint(0, h), np.random.randint(0, w)
                    r = max(1, h // 20)
                    y, x = np.ogrid[-cy:h-cy, -cx:w-cx]
                    region = x*x + y*y <= r*r
                    result[region] = np.nan
    
    return result


def extract_patch(
    data: np.ndarray,
    center_lon: float = 0.0,
    center_lat: float = 90.0,
    patch_size: int = 64
) -> np.ndarray:
    """
    Extract a square patch from a HEALPix map or 2D array.
    
    For 1D HEALPix maps: uses gnomonic projection centered at (lon, lat).
    For 2D arrays: extracts a centered sub-patch.
    
    Args:
        data: Input data (1D HEALPix map or 2D array)
        center_lon: Center longitude in degrees
        center_lat: Center latitude in degrees  
        patch_size: Size of the square patch (NxN pixels)
    
    Returns:
        2D numpy array of shape (patch_size, patch_size)
    """
    if data.ndim == 1 and HEALPY_AVAILABLE:
        # HEALPix map → gnomonic projection
        nside = hp.npix2nside(len(data))
        patch = hp.gnomview(
            data,
            rot=(center_lon, center_lat),
            xsize=patch_size,
            ysize=patch_size,
            reso=3.0,  # arcmin per pixel
            return_projected_map=True,
            no_plot=True,
        )
        return patch
    elif data.ndim == 2:
        # 2D array → extract centered sub-patch
        h, w = data.shape
        if patch_size >= min(h, w):
            return data
        
        cy, cx = h // 2, w // 2
        half = patch_size // 2
        return data[cy - half:cy + half, cx - half:cx + half]
    else:
        # Without healpy for gnomonic projection, fallback to a naive flat extraction for demo
        if data.ndim == 1:
            total_needed = patch_size * patch_size
            if len(data) >= total_needed:
                return data[:total_needed].reshape((patch_size, patch_size))
            else:
                padded = np.zeros(total_needed)
                padded[:len(data)] = data
                return padded.reshape((patch_size, patch_size))
        elif data.ndim >= 2:
            return data[:patch_size, :patch_size]
        return data

def normalize_patch(data: np.ndarray, method: str = "zscore") -> np.ndarray:
    """
    Normalize a data patch.
    
    Args:
        data: Input 2D array
        method: Normalization method - 'zscore', 'minmax', or 'none'
    
    Returns:
        Normalized array
    """
    result = data.copy().astype(np.float64)
    valid = ~np.isnan(result)
    
    if not np.any(valid):
        return result
    
    if method == "zscore":
        mean = np.nanmean(result)
        std = np.nanstd(result)
        if std > 0:
            result[valid] = (result[valid] - mean) / std
    elif method == "minmax":
        vmin = np.nanmin(result)
        vmax = np.nanmax(result)
        if vmax > vmin:
            result[valid] = (result[valid] - vmin) / (vmax - vmin)
    
    return result


def apply_wavelet_filter(data: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """
    Apply a simplified wavelet/needlet-like filter to the data.
    Uses Gaussian smoothing as a simplified needlet-like scale decomposition.
    
    Args:
        data: Input 2D array
        scale: Filter scale (sigma for Gaussian smoothing)
    
    Returns:
        Filtered array
    """
    if not SCIPY_AVAILABLE:
        return data
    
    result = data.copy()
    
    # Replace NaNs with zeros for filtering
    nan_mask = np.isnan(result)
    result[nan_mask] = 0
    
    # Gaussian smoothing as simplified needlet-like filter
    # Larger scale = smoother (large-scale features)
    smoothed = gaussian_filter(result, sigma=scale)
    
    # Needlet-like: difference between two scales (band-pass)
    if scale > 0.5:
        large_scale = gaussian_filter(result, sigma=scale * 2)
        result = smoothed - large_scale  # Band-pass filter
    else:
        result = smoothed
    
    # Restore NaN mask
    result[nan_mask] = np.nan
    
    return result


def preprocess_pipeline(
    data: np.ndarray,
    apply_mask: bool = True,
    mask: Optional[np.ndarray] = None,
    mask_type: str = "galactic",
    patch_center_lon: float = 0.0,
    patch_center_lat: float = 90.0,
    patch_size: int = 64,
    normalize: bool = True,
    apply_filter: bool = False,
    filter_scale: float = 1.0,
) -> dict:
    """
    Run the full preprocessing pipeline on CMB map data.
    
    Returns dict with:
      - 'patch': preprocessed 2D numpy array
      - 'stats': pixel statistics
      - 'metadata': preprocessing info
    """
    settings = get_settings()
    
    # Step 1: Extract patch
    patch = extract_patch(data, patch_center_lon, patch_center_lat, patch_size)
    
    # Step 2: Apply mask
    mask_applied = False
    if apply_mask:
        patch = apply_map_mask(patch, mask, mask_type)
        mask_applied = True
    
    # Step 3: Apply filter
    filter_applied = False
    if apply_filter and SCIPY_AVAILABLE:
        patch = apply_wavelet_filter(patch, scale=filter_scale)
        filter_applied = True
    
    # Step 4: Normalize
    if normalize:
        patch = normalize_patch(patch, method="zscore")
    
    # Replace remaining NaN with 0 for TDA compatibility
    patch_clean = np.nan_to_num(patch, nan=0.0)
    
    # Compute stats
    valid = ~np.isnan(patch) if np.any(np.isnan(patch)) else np.ones_like(patch, dtype=bool)
    stats = {
        "min": float(np.nanmin(patch)),
        "max": float(np.nanmax(patch)),
        "mean": float(np.nanmean(patch)),
        "std": float(np.nanstd(patch)),
        "shape": list(patch_clean.shape),
        "valid_pixels": int(np.sum(valid)),
        "total_pixels": int(patch.size),
    }
    
    return {
        "patch": patch_clean,
        "stats": stats,
        "mask_applied": mask_applied,
        "filter_applied": filter_applied,
        "metadata": {
            "patch_size": patch_size,
            "center_lon": patch_center_lon,
            "center_lat": patch_center_lat,
            "normalize": normalize,
            "filter_scale": filter_scale if filter_applied else None,
        },
    }
