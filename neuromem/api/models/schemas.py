"""
NeuraMem API Models and Schemas
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BeliefBase(BaseModel):
    """Base model for beliefs."""
    content: str = Field(..., min_length=1, description="The belief content")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BeliefCreate(BeliefBase):
    """Model for creating a belief."""
    pass


class BeliefUpdate(BaseModel):
    """Model for updating a belief."""
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BeliefResponse(BeliefBase):
    """Model for belief response."""
    belief_id: str
    created_at: datetime
    current_confidence: float


class RejectionReason(str, Enum):
    """Rejection reason options."""
    CONTRADICTION = "contradiction"
    LOW_CONFIDENCE = "low_confidence"
    EXPLICIT_REJECTION = "explicit_rejection"
    OBSOLETE = "obsolete"
    USER_REJECTED = "user_rejected"


class RejectionCreate(BaseModel):
    """Model for creating a rejection."""
    content: str
    reason: RejectionReason
    belief_id: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class RejectionResponse(BaseModel):
    """Model for rejection response."""
    id: str
    content: str
    reason: str
    created_at: datetime


class ContradictionResponse(BaseModel):
    """Model for contradiction response."""
    id: str
    belief_ids: List[str]
    type: str
    severity: str
    description: str
    resolved: bool


class TraceStep(BaseModel):
    """Model for a reasoning trace step."""
    operation: str
    inputs: List[str]
    output: str
    confidence: float = Field(ge=0.0, le=1.0)
    inference_type: str


class TraceCreate(BaseModel):
    """Model for creating a reasoning trace."""
    initial_beliefs: List[str]
    tags: Optional[List[str]] = None


class TraceStepAdd(BaseModel):
    """Model for adding a step to a trace."""
    operation: str
    inputs: List[str]
    output: str
    confidence: float = Field(ge=0.0, le=1.0)
    inference_type: str = "deductive"


class TraceComplete(BaseModel):
    """Model for completing a trace."""
    conclusion: str


class TraceResponse(BaseModel):
    """Model for trace response."""
    trace_id: str
    status: str
    conclusion: Optional[str] = None
    step_count: int
    overall_confidence: float


class AuditEventCreate(BaseModel):
    """Model for creating an audit event."""
    event_type: str
    description: str
    actor_id: Optional[str] = None
    affected_entities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditEventResponse(BaseModel):
    """Model for audit event response."""
    event_id: str
    event_type: str
    timestamp: datetime
    description: str


class ExportFormat(str, Enum):
    """Export format options."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    MARKDOWN = "markdown"


class ExportRequest(BaseModel):
    """Model for export requests."""
    format: ExportFormat = ExportFormat.JSON
    limit: int = Field(default=1000, le=10000)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "0.1.0"


class StatsResponse(BaseModel):
    """Generic stats response."""
    data: Dict[str, Any]
