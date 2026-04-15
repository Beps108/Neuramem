"""
NeuraMem Traces API Routes
Endpoints for managing reasoning traces.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from neuromem.core.reasoning_trace import get_reasoning_tracer, InferenceType

router = APIRouter()


@router.post("/")
async def create_trace(initial_beliefs: List[str], tags: Optional[List[str]] = None):
    """Create a new reasoning trace."""
    tracer = get_reasoning_tracer()
    trace = tracer.create_trace(initial_beliefs=initial_beliefs, tags=tags)
    
    return {"trace_id": trace.trace_id, "status": "active"}


@router.post("/{trace_id}/step")
async def add_step(
    trace_id: str,
    operation: str,
    inputs: List[str],
    output: str,
    confidence: float = 1.0,
    inference_type: str = "deductive"
):
    """Add a step to a reasoning trace."""
    tracer = get_reasoning_tracer()
    
    try:
        itype = InferenceType(inference_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid inference type")
    
    step = tracer.add_step(
        trace_id=trace_id,
        operation=operation,
        inputs=inputs,
        output=output,
        confidence=confidence,
        inference_type=itype
    )
    
    if not step:
        raise HTTPException(status_code=404, detail="Trace not found or not active")
    
    return {"step_id": step.step_id, "output": step.output}


@router.post("/{trace_id}/complete")
async def complete_trace(trace_id: str, conclusion: str):
    """Complete a reasoning trace with a conclusion."""
    tracer = get_reasoning_tracer()
    
    if not tracer.complete_trace(trace_id, conclusion):
        raise HTTPException(status_code=404, detail="Trace not found or not active")
    
    return {"message": "Trace completed", "conclusion": conclusion}


@router.get("/{trace_id}")
async def get_trace(trace_id: str, format: str = "json"):
    """Get a reasoning trace."""
    tracer = get_reasoning_tracer()
    trace = tracer.get_trace(trace_id)
    
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    return tracer.export_trace(trace_id, format=format)


@router.get("/")
async def list_traces(active_only: bool = False):
    """List reasoning traces."""
    tracer = get_reasoning_tracer()
    
    if active_only:
        traces = tracer.get_active_traces()
    else:
        traces = list(tracer._traces.values())
    
    return [t.to_dict() for t in traces]


@router.get("/stats")
async def get_stats():
    """Get trace statistics."""
    tracer = get_reasoning_tracer()
    return tracer.stats()
