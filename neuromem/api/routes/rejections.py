"""
NeuraMem Rejections API Routes
Endpoints for managing rejected beliefs.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from neuromem.core.negative_memory import get_negative_store, RejectionReason

router = APIRouter()


@router.post("/")
async def create_rejection(
    content: str,
    reason: str = "contradiction",
    belief_id: Optional[str] = None,
    confidence: float = 0.0,
    tags: Optional[List[str]] = None
):
    """Reject a belief."""
    store = get_negative_store()
    
    try:
        rejection_reason = RejectionReason(reason)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid reason. Must be one of: {[r.value for r in RejectionReason]}")
    
    mem_id = store.reject_belief(
        content=content,
        reason=rejection_reason,
        belief_id=belief_id,
        confidence=confidence,
        tags=tags
    )
    
    return {"id": mem_id, "status": "rejected"}


@router.get("/{memory_id}")
async def get_rejection(memory_id: str):
    """Get a rejected memory by ID."""
    store = get_negative_store()
    memory = store.get(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Rejection not found")
    
    return memory.to_dict()


@router.get("/")
async def list_rejections(reason: Optional[str] = None, tag: Optional[str] = None):
    """List rejected memories."""
    store = get_negative_store()
    
    if reason:
        try:
            rejection_reason = RejectionReason(reason)
            memories = store.get_by_reason(rejection_reason)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid reason")
    elif tag:
        memories = store.get_by_tag(tag)
    else:
        memories = list(store._memories.values())
    
    return [m.to_dict() for m in memories]


@router.get("/search")
async def search_rejections(query: str):
    """Search rejected memories by content."""
    store = get_negative_store()
    results = store.search(query)
    return [m.to_dict() for m in results]


@router.delete("/{memory_id}")
async def remove_rejection(memory_id: str):
    """Remove a rejection."""
    store = get_negative_store()
    
    if not store.remove(memory_id):
        raise HTTPException(status_code=404, detail="Rejection not found")
    
    return {"message": f"Rejection {memory_id} removed"}


@router.get("/stats")
async def get_stats():
    """Get rejection statistics."""
    store = get_negative_store()
    return store.stats()
