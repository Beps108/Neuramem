"""
NeuraMem Contradictions API Routes
Endpoints for managing contradictions.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from neuromem.core.contradiction import get_contradiction_store

router = APIRouter()


@router.get("/")
async def list_contradictions(resolved: Optional[bool] = None):
    """List contradictions."""
    store = get_contradiction_store()
    
    if resolved is True:
        contradictions = [c for c in store._contradictions.values() if c.resolved]
    elif resolved is False:
        contradictions = store.get_unresolved()
    else:
        contradictions = list(store._contradictions.values())
    
    return [c.to_dict() for c in contradictions]


@router.get("/{contradiction_id}")
async def get_contradiction(contradiction_id: str):
    """Get a contradiction by ID."""
    store = get_contradiction_store()
    
    # Search for the contradiction
    for cid, con in store._contradictions.items():
        if cid == contradiction_id or con.get_id() == contradiction_id:
            return con.to_dict()
    
    raise HTTPException(status_code=404, detail="Contradiction not found")


@router.post("/{contradiction_id}/resolve")
async def resolve_contradiction(contradiction_id: str, notes: Optional[str] = None):
    """Resolve a contradiction."""
    store = get_contradiction_store()
    
    # Find and resolve
    for cid, con in store._contradictions.items():
        if cid == contradiction_id or con.get_id() == contradiction_id:
            if store.resolve(con.get_id(), notes):
                return {"message": "Contradiction resolved", "id": con.get_id()}
    
    raise HTTPException(status_code=404, detail="Contradiction not found")


@router.get("/stats")
async def get_stats():
    """Get contradiction statistics."""
    store = get_contradiction_store()
    return store.stats()
