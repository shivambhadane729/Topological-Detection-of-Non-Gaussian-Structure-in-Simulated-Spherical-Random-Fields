"""
CosmoPH - Dataset Schemas
Pydantic models for dataset-related request/response objects.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DatasetCategory(str, Enum):
    RAW = "raw"
    SAMPLE = "sample"
    PROCESSED = "processed"
    EXTERNAL = "external"


class DatasetInfo(BaseModel):
    """Information about a single dataset."""
    id: str = Field(..., description="Unique dataset identifier")
    name: str = Field(..., description="Human-readable dataset name")
    filename: str = Field(..., description="File name on disk")
    category: DatasetCategory = Field(..., description="Dataset category")
    description: str = Field("", description="Dataset description")
    file_size_mb: Optional[float] = Field(None, description="File size in MB")
    nside: Optional[int] = Field(None, description="HEALPix NSIDE parameter")
    is_available: bool = Field(True, description="Whether the file exists on disk")
    source_url: Optional[str] = Field(None, description="Download URL")


class DatasetListResponse(BaseModel):
    """Response containing list of available datasets."""
    datasets: list[DatasetInfo]
    total: int


class DatasetSelectRequest(BaseModel):
    """Request to select a dataset for processing."""
    dataset_id: str = Field(..., description="Dataset ID to select")
