"""
CosmoPH - Gaussian Generator Service
Generates synthetic Gaussian random fields for null hypothesis comparison.
"""

import numpy as np
from typing import Optional

try:
    from scipy.ndimage import gaussian_filter
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import healpy as hp
    HEALPY_AVAILABLE = True
except ImportError:
    HEALPY_AVAILABLE = False


def generate_gaussian_field(
    shape: tuple = (64, 64),
    mean: float = 0.0,
    std: float = 1e-5,
    correlation_length: float = 2.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Generate a 2D Gaussian random field with spatial correlations.
    
    Mimics a CMB-like Gaussian field by generating white noise and
    smoothing with a Gaussian kernel.
    
    Args:
        shape: Output shape (height, width)
        mean: Mean of the field
        std: Standard deviation of the field
        correlation_length: Spatial correlation scale in pixels
        seed: Random seed for reproducibility
    
    Returns:
        2D numpy array
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate white noise
    white_noise = np.random.normal(0, 1, shape)
    
    if SCIPY_AVAILABLE and correlation_length > 0:
        # Apply Gaussian smoothing for spatial correlations
        field = gaussian_filter(white_noise, sigma=correlation_length)
        # Renormalize to desired statistics
        field = (field - field.mean()) / max(field.std(), 1e-15) * std + mean
    else:
        field = white_noise * std + mean
    
    return field


def generate_non_gaussian_field(
    shape: tuple = (64, 64),
    mean: float = 0.0,
    std: float = 1e-5,
    f_nl: float = 100.0,
    correlation_length: float = 2.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Generate a non-Gaussian field with local-type non-Gaussianity.
    
    Uses the local ansatz: Φ = φ + f_NL * (φ² - <φ²>)
    where φ is a Gaussian field.
    
    Args:
        shape: Output shape
        mean: Mean amplitude
        std: Standard deviation
        f_nl: Non-linearity parameter (larger = more non-Gaussian)
        correlation_length: Spatial correlation scale
        seed: Random seed
    
    Returns:
        2D numpy array with non-Gaussian features
    """
    gaussian_part = generate_gaussian_field(shape, 0.0, std, correlation_length, seed)
    
    # Local-type non-Gaussianity
    phi_squared = gaussian_part ** 2
    phi_squared_mean = np.mean(phi_squared)
    
    # f_NL scaling (normalized)
    ng_correction = f_nl * (phi_squared - phi_squared_mean) * (std / max(np.std(phi_squared), 1e-15))
    
    result = gaussian_part + ng_correction + mean
    
    return result


def generate_healpix_gaussian(nside: int = 64, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate a Gaussian random HEALPix map with a CMB-like power spectrum.
    
    Args:
        nside: HEALPix NSIDE parameter
        seed: Random seed
    
    Returns:
        1D HEALPix map array
    """
    if not HEALPY_AVAILABLE:
        # Fallback: flat Gaussian field
        npix = 12 * nside ** 2
        if seed is not None:
            np.random.seed(seed)
        return np.random.normal(0, 1e-5, npix)
    
    if seed is not None:
        np.random.seed(seed)
    
    # Simple CMB-like power spectrum: C_l ∝ 1/l(l+1)
    lmax = 3 * nside - 1
    ell = np.arange(lmax + 1)
    cl = np.zeros(lmax + 1)
    cl[2:] = 1e-10 / (ell[2:] * (ell[2:] + 1))  # CMB-like spectrum
    
    # Generate map from power spectrum
    alm = hp.synalm(cl, lmax=lmax)
    healpix_map = hp.alm2map(alm, nside, verbose=False)
    
    return healpix_map
