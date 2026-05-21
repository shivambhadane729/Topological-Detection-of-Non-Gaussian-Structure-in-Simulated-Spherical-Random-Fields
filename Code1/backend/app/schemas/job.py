"""
CosmoPH - Job Schemas
Pydantic models for async job tracking.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreate(BaseModel):
    """Internal model for creating a new job."""
    job_type: str
    parameters: dict = Field(default_factory=dict)


class JobResponse(BaseModel):
    """Response with job information."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    job_type: str = Field(..., description="Type of job")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    progress: float = Field(0.0, description="Progress 0-100")
    message: str = Field("", description="Status message")
    result: Optional[Any] = Field(None, description="Job result data")
    error: Optional[str] = Field(None, description="Error message if failed")
