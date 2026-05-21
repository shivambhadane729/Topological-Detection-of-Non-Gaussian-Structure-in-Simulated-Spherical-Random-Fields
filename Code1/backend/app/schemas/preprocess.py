"""
CosmoPH - Preprocessing Schemas
Pydantic models for preprocessing configuration and results.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PreprocessConfig(BaseModel):
    """Configuration for preprocessing a CMB map."""
    dataset_id: str = Field(..., description="ID of dataset to preprocess")
    apply_mask: bool = Field(True, description="Apply galactic plane mask")
    mask_type: str = Field("galactic", description="Mask type: galactic, point_source, custom")
    patch_center_lon: float = Field(0.0, description="Patch center longitude (degrees)")
    patch_center_lat: float = Field(90.0, description="Patch center latitude (degrees)")
    patch_size: int = Field(64, description="Patch size in pixels (NxN)")
    normalize: bool = Field(True, description="Normalize pixel values")
    apply_filter: bool = Field(False, description="Apply wavelet/needlet filter")
    filter_scale: float = Field(1.0, description="Filter scale parameter")
    target_nside: int = Field(64, description="Target NSIDE for downsampling")


class PreprocessResult(BaseModel):
    """Result of preprocessing step."""
    job_id: str
    dataset_id: str
    patch_shape: list[int] = Field(..., description="Shape of extracted patch")
    pixel_stats: dict = Field(..., description="min, max, mean, std of patch")
    mask_applied: bool
    filter_applied: bool
    preview_data: Optional[list[list[float]]] = Field(None, description="2D array for heatmap preview")
    message: str = Field("Preprocessing completed successfully")
