from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Preprocessing Schemas ---
class PreprocessRequest(BaseModel):
    map_id: str = Field(..., description="ID of the uploaded CMB map")
    mask_galactic_plane: bool = Field(False, description="Whether to mask the galactic plane")
    mask_point_sources: bool = Field(False, description="Whether to mask point sources")
    scale: Optional[float] = Field(None, description="Scale parameter for wavelet/needlet filtering")

class PreprocessResponse(BaseModel):
    job_id: str
    status: str
    message: str

# --- TDA Computation Schemas ---
class TDARequest(BaseModel):
    map_id: str = Field(..., description="ID of the preprocessed map")
    max_dimension: int = Field(2, description="Maximum homology dimension to compute (0, 1, 2)")
    threshold: Optional[float] = Field(None, description="Threshold for persistent homology")

class TDAResponse(BaseModel):
    job_id: str
    status: str
    message: str

# --- Result Schemas ---
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PersistenceDiagram(BaseModel):
    dimension: int
    birth: float
    death: float

class TDAResultData(BaseModel):
    diagrams: List[PersistenceDiagram]
    betti_curves: Dict[int, List[float]]
    fnl_prediction: Optional[float] = None
    classification: Optional[str] = None
    confidence_score: Optional[float] = None
