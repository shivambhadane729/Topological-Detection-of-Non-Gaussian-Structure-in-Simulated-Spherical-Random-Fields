"""
CosmoPH - TDA Schemas
Pydantic models for TDA computation requests and results.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TDAConfig(BaseModel):
    """Configuration for TDA computation."""
    job_id: str = Field(..., description="Preprocessed data job ID")
    max_dimension: int = Field(1, description="Max homology dimension (0=components, 1=loops)")
    max_edge_length: float = Field(2.0, description="Maximum edge length for Rips complex")
    max_points: int = Field(1000, description="Maximum number of points to subsample")
    compute_betti: bool = Field(True, description="Compute Betti curves")
    compute_persistence_image: bool = Field(True, description="Compute persistence images")
    compare_gaussian: bool = Field(True, description="Compare against Gaussian null sample")
    n_gaussian_samples: int = Field(5, description="Number of Gaussian null samples for comparison")


class PersistencePair(BaseModel):
    """A single persistence pair (birth, death)."""
    birth: float
    death: float
    dimension: int


class TDAResult(BaseModel):
    """Result of TDA computation."""
    job_id: str
    status: str = "completed"
    
    # Persistence diagram data
    persistence_diagram: list[PersistencePair] = Field(
        default_factory=list,
        description="List of persistence pairs"
    )
    
    # Betti curves
    betti_curves: Optional[dict] = Field(
        None,
        description="Betti curves: {dimension: {thresholds: [...], counts: [...]}}"
    )
    
    # Persistence image
    persistence_image: Optional[list[list[float]]] = Field(
        None,
        description="2D persistence image as nested array"
    )
    
    # Gaussian comparison
    gaussian_comparison: Optional[dict] = Field(
        None, 
        description="Comparison metrics: wasserstein_distances, p_values, is_non_gaussian"
    )
    
    # Summary stats
    summary: Optional[dict] = Field(
        None,
        description="Summary statistics: total_features, max_persistence, mean_persistence"
    )
    
    # Map preview
    map_preview: Optional[list[list[float]]] = Field(
        None,
        description="Original CMB patch for visualization"
    )
    
    message: str = "TDA computation completed"
