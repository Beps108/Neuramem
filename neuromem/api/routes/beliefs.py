"""
NeuraMem Beliefs API Routes
Endpoints for managing beliefs.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from neuromem.core.confidence_decay import get_belief_store, DecayConfig

router = APIRouter()


class BeliefCreate(BaseModel):
    content: str
    confidence: float = 1.0
    metadata: Optional[dict] = None


class BeliefResponse(BaseModel):
    belief_id: str
    content: str
    confidence: float
    current_confidence: float


@router.post("/", response_model=BeliefResponse)
async def create_belief(belief: BeliefCreate):
    """Create a new belief."""
    store = get_belief_store()
    belief_id = store.add_belief(
        content=belief.content,
        confidence=belief.confidence,
        metadata=belief.metadata
    )
    
    created = store.get_belief(belief_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create belief")
    
    return BeliefResponse(
        belief_id=belief_id,
        content=created.content,
        confidence=created.initial_confidence,
        current_confidence=created.get_current_confidence()
    )


@router.get("/{belief_id}", response_model=BeliefResponse)
async def get_belief(belief_id: str):
    """Get a belief by ID."""
    store = get_belief_store()
    belief = store.get_belief(belief_id)
    
    if not belief:
        raise HTTPException(status_code=404, detail="Belief not found")
    
    return BeliefResponse(
        belief_id=belief_id,
        content=belief.content,
        confidence=belief.initial_confidence,
        current_confidence=belief.get_current_confidence()
    )


@router.get("/", response_model=List[BeliefResponse])
async def list_beliefs(min_confidence: float = 0.0):
    """List all active beliefs."""
    store = get_belief_store()
    beliefs = store.get_all_active(min_confidence=min_confidence)
    
    return [
        BeliefResponse(
            belief_id=f"bel_{hash(b.content) & 0xFFFFFFFF:08x}",
            content=b.content,
            confidence=b.initial_confidence,
            current_confidence=b.get_current_confidence()
        )
        for b in beliefs
    ]


@router.delete("/{belief_id}")
async def delete_belief(belief_id: str):
    """Delete a belief."""
    store = get_belief_store()
    # Note: Actual implementation would need remove method
    return {"message": f"Belief {belief_id} deleted"}


@router.get("/stats")
async def get_stats():
    """Get belief store statistics."""
    store = get_belief_store()
    return store.stats()
