"""
CosmoPH - Export Schemas
Pydantic models for export/download endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ExportFormat(str, Enum):
    PNG = "png"
    SVG = "svg"
    CSV = "csv"
    JSON = "json"
    ZIP = "zip"


class ExportRequest(BaseModel):
    """Request to export results."""
    job_id: str = Field(..., description="Job ID to export results for")
    formats: list[ExportFormat] = Field(
        default=[ExportFormat.ZIP],
        description="Export formats to generate"
    )
    include_plots: bool = Field(True, description="Include plot images")
    include_data: bool = Field(True, description="Include raw data files")
    include_report: bool = Field(True, description="Include summary report")


class ExportResponse(BaseModel):
    """Response with export file information."""
    job_id: str
    export_id: str
    files: list[dict] = Field(
        ...,
        description="List of exported files with name, format, size, url"
    )
    zip_url: Optional[str] = Field(None, description="URL to download ZIP bundle")
    message: str = "Export completed"
