"""
NeuraMem Audit API Routes
Endpoints for audit logging and export.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from neuromem.core.audit_exporter import (
    get_audit_exporter, 
    AuditEventType, 
    ExportFormat
)

router = APIRouter()


@router.post("/log")
async def log_event(
    event_type: str,
    description: str,
    actor_id: Optional[str] = None,
    affected_entities: Optional[List[str]] = None,
    metadata: Optional[dict] = None
):
    """Log an audit event."""
    exporter = get_audit_exporter()
    
    try:
        etype = AuditEventType(event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event type")
    
    event_id = exporter.logger.log(
        event_type=etype,
        description=description,
        actor_id=actor_id,
        affected_entities=affected_entities,
        metadata=metadata
    )
    
    return {"event_id": event_id, "status": "logged"}


@router.get("/events")
async def get_events(
    limit: int = Query(default=100, le=1000),
    event_type: Optional[str] = None,
    actor_id: Optional[str] = None
):
    """Get audit events."""
    exporter = get_audit_exporter()
    
    etype = None
    if event_type:
        try:
            etype = AuditEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid event type")
    
    events = exporter.logger.get_events(
        event_type=etype,
        actor_id=actor_id,
        limit=limit
    )
    
    return [e.to_dict() for e in events]


@router.get("/export")
async def export_audit(
    format: str = Query(default="json"),
    limit: int = Query(default=1000, le=10000)
):
    """Export audit logs."""
    exporter = get_audit_exporter()
    
    try:
        fmt = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    content = exporter.export(format=fmt, limit=limit)
    
    media_types = {
        "json": "application/json",
        "csv": "text/csv",
        "xml": "application/xml",
        "markdown": "text/markdown"
    }
    
    return {"content": content, "media_type": media_types.get(format, "application/json")}


@router.get("/compliance-report")
async def get_compliance_report(period_days: int = 30):
    """Generate compliance report."""
    from neuromem.core.audit_exporter import ComplianceReporter
    
    exporter = get_audit_exporter()
    reporter = ComplianceReporter(exporter)
    
    report = reporter.generate_report(period_days=period_days)
    return report


@router.get("/stats")
async def get_stats():
    """Get audit statistics."""
    exporter = get_audit_exporter()
    return {"event_count": exporter.logger.count()}
