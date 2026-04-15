"""
NeuraMem Negative Memory Module (Feature 1)
Stores and manages rejected beliefs, false memories, and negative constraints.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib


class RejectionReason(Enum):
    """Reasons for rejecting a belief or memory."""
    CONTRADICTION = "contradiction"
    LOW_CONFIDENCE = "low_confidence"
    EXPLICIT_REJECTION = "explicit_rejection"
    OBSOLETE = "obsolete"
    USER_REJECTED = "user_rejected"
    LOGICAL_INCONSISTENCY = "logical_inconsistency"


@dataclass
class NegativeMemory:
    """Represents a rejected belief or negative memory."""
    
    content: str
    rejection_reason: RejectionReason
    original_belief_id: Optional[str] = None
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def get_id(self) -> str:
        """Generate a unique ID for this negative memory."""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        return f"neg_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.get_id(),
            "content": self.content,
            "rejection_reason": self.rejection_reason.value,
            "original_belief_id": self.original_belief_id,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NegativeMemory":
        """Create from dictionary representation."""
        return cls(
            content=data["content"],
            rejection_reason=RejectionReason(data["rejection_reason"]),
            original_belief_id=data.get("original_belief_id"),
            confidence_score=data.get("confidence_score", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            metadata=data.get("metadata", {}),
            tags=data.get("tags", [])
        )


class NegativeMemoryStore:
    """Storage and retrieval system for negative memories."""
    
    def __init__(self):
        self._memories: Dict[str, NegativeMemory] = {}
        self._index_by_reason: Dict[RejectionReason, List[str]] = {r: [] for r in RejectionReason}
        self._index_by_tag: Dict[str, List[str]] = {}
    
    def add(self, memory: NegativeMemory) -> str:
        """Add a negative memory to the store."""
        mem_id = memory.get_id()
        
        if mem_id in self._memories:
            return mem_id
        
        self._memories[mem_id] = memory
        
        # Index by reason
        self._index_by_reason[memory.rejection_reason].append(mem_id)
        
        # Index by tags
        for tag in memory.tags:
            if tag not in self._index_by_tag:
                self._index_by_tag[tag] = []
            self._index_by_tag[tag].append(mem_id)
        
        return mem_id
    
    def reject_belief(self, content: str, reason: RejectionReason, 
                     belief_id: Optional[str] = None, 
                     confidence: float = 0.0,
                     tags: Optional[List[str]] = None) -> str:
        """Convenience method to reject a belief."""
        memory = NegativeMemory(
            content=content,
            rejection_reason=reason,
            original_belief_id=belief_id,
            confidence_score=confidence,
            tags=tags or []
        )
        return self.add(memory)
    
    def get(self, memory_id: str) -> Optional[NegativeMemory]:
        """Retrieve a negative memory by ID."""
        return self._memories.get(memory_id)
    
    def get_by_reason(self, reason: RejectionReason) -> List[NegativeMemory]:
        """Get all negative memories with a specific rejection reason."""
        ids = self._index_by_reason.get(reason, [])
        return [self._memories[mid] for mid in ids if mid in self._memories]
    
    def get_by_tag(self, tag: str) -> List[NegativeMemory]:
        """Get all negative memories with a specific tag."""
        ids = self._index_by_tag.get(tag, [])
        return [self._memories[mid] for mid in ids if mid in self._memories]
    
    def search(self, query: str) -> List[NegativeMemory]:
        """Search negative memories by content."""
        query_lower = query.lower()
        results = []
        for memory in self._memories.values():
            if query_lower in memory.content.lower():
                results.append(memory)
        return results
    
    def is_rejected(self, content: str) -> bool:
        """Check if content has been rejected."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        potential_id = f"neg_{content_hash}"
        return potential_id in self._memories
    
    def remove(self, memory_id: str) -> bool:
        """Remove a negative memory from the store."""
        if memory_id not in self._memories:
            return False
        
        memory = self._memories[memory_id]
        
        # Remove from reason index
        if memory_id in self._index_by_reason[memory.rejection_reason]:
            self._index_by_reason[memory.rejection_reason].remove(memory_id)
        
        # Remove from tag indexes
        for tag in memory.tags:
            if tag in self._index_by_tag and memory_id in self._index_by_tag[tag]:
                self._index_by_tag[tag].remove(memory_id)
        
        del self._memories[memory_id]
        return True
    
    def count(self) -> int:
        """Get total count of negative memories."""
        return len(self._memories)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the negative memory store."""
        reason_counts = {r.value: len(ids) for r, ids in self._index_by_reason.items()}
        return {
            "total_count": self.count(),
            "by_reason": reason_counts,
            "unique_tags": len(self._index_by_tag),
            "oldest": min((m.created_at for m in self._memories.values()), default=None),
            "newest": max((m.created_at for m in self._memories.values()), default=None)
        }


# Global instance
_negative_store: Optional[NegativeMemoryStore] = None


def get_negative_store() -> NegativeMemoryStore:
    """Get the global negative memory store instance."""
    global _negative_store
    if _negative_store is None:
        _negative_store = NegativeMemoryStore()
    return _negative_store


if __name__ == "__main__":
    store = get_negative_store()
    
    # Test rejection
    mem_id = store.reject_belief(
        "The Earth is flat",
        RejectionReason.CONTRADICTION,
        belief_id="bel_123",
        confidence=0.95,
        tags=["science", "geography"]
    )
    
    print(f"Rejected memory ID: {mem_id}")
    print(f"Is rejected: {store.is_rejected('The Earth is flat')}")
    print(f"Stats: {store.stats()}")
    
    # Retrieve
    memory = store.get(mem_id)
    if memory:
        print(f"Content: {memory.content}")
        print(f"Reason: {memory.rejection_reason.value}")
