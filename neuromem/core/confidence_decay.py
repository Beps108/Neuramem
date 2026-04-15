"""
NeuraMem Confidence Decay Module (Feature 2)
Implements time-based confidence decay for beliefs and memories.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import math


class DecayFunction(Enum):
    """Types of decay functions available."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    STEP = "step"


@dataclass
class DecayConfig:
    """Configuration for confidence decay behavior."""
    
    function: DecayFunction = DecayFunction.EXPONENTIAL
    half_life_hours: float = 24.0  # Time for confidence to halve
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    decay_rate: float = 0.1  # Used for linear/step decay
    step_intervals_hours: List[float] = field(default_factory=lambda: [24, 48, 72, 168])
    step_values: List[float] = field(default_factory=lambda: [0.9, 0.7, 0.5, 0.3])
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.min_confidence < 0 or self.max_confidence > 1:
            return False
        if self.min_confidence >= self.max_confidence:
            return False
        if self.half_life_hours <= 0:
            return False
        return True


class ConfidenceDecay:
    """Calculates and applies confidence decay over time."""
    
    def __init__(self, config: Optional[DecayConfig] = None):
        self.config = config or DecayConfig()
        if not self.config.validate():
            raise ValueError("Invalid decay configuration")
    
    def calculate_decay(self, initial_confidence: float, 
                       created_at: datetime,
                       current_time: Optional[datetime] = None) -> float:
        """Calculate the current confidence after decay."""
        current_time = current_time or datetime.now()
        elapsed = current_time - created_at
        elapsed_hours = elapsed.total_seconds() / 3600
        
        if elapsed_hours <= 0:
            return initial_confidence
        
        decayed = self._apply_decay(initial_confidence, elapsed_hours)
        
        # Clamp to valid range
        return max(
            self.config.min_confidence,
            min(self.config.max_confidence, decayed)
        )
    
    def _apply_decay(self, initial: float, elapsed_hours: float) -> float:
        """Apply the configured decay function."""
        if self.config.function == DecayFunction.LINEAR:
            return self._linear_decay(initial, elapsed_hours)
        elif self.config.function == DecayFunction.EXPONENTIAL:
            return self._exponential_decay(initial, elapsed_hours)
        elif self.config.function == DecayFunction.LOGARITHMIC:
            return self._logarithmic_decay(initial, elapsed_hours)
        elif self.config.function == DecayFunction.STEP:
            return self._step_decay(initial, elapsed_hours)
        else:
            return initial
    
    def _linear_decay(self, initial: float, elapsed_hours: float) -> float:
        """Linear decay: confidence decreases at a constant rate."""
        decay_amount = elapsed_hours * self.config.decay_rate
        return initial - decay_amount
    
    def _exponential_decay(self, initial: float, elapsed_hours: float) -> float:
        """Exponential decay: confidence halves every half_life period."""
        half_lives = elapsed_hours / self.config.half_life_hours
        return initial * (0.5 ** half_lives)
    
    def _logarithmic_decay(self, initial: float, elapsed_hours: float) -> float:
        """Logarithmic decay: rapid initial decay that slows over time."""
        if elapsed_hours < 1:
            return initial
        decay_factor = math.log(elapsed_hours + 1) / math.log(self.config.half_life_hours + 1)
        return initial * (1 - decay_factor * (1 - self.config.min_confidence))
    
    def _step_decay(self, initial: float, elapsed_hours: float) -> float:
        """Step decay: confidence drops at specific intervals."""
        for i, interval in enumerate(self.config.step_intervals_hours):
            if elapsed_hours >= interval:
                if i < len(self.config.step_values):
                    return initial * self.config.step_values[i]
        return initial
    
    def get_half_life(self) -> timedelta:
        """Get the half-life as a timedelta."""
        return timedelta(hours=self.config.half_life_hours)
    
    def time_to_threshold(self, initial_confidence: float, 
                         threshold: float) -> Optional[timedelta]:
        """Calculate time until confidence reaches a threshold."""
        if threshold >= initial_confidence:
            return timedelta(0)
        if threshold <= self.config.min_confidence:
            return None
        
        # Binary search for time
        low, high = 0, self.config.half_life_hours * 10
        
        for _ in range(50):  # Precision limit
            mid = (low + high) / 2
            confidence = self.calculate_decay(
                initial_confidence,
                datetime.now(),
                datetime.now() + timedelta(hours=mid)
            )
            
            if abs(confidence - threshold) < 0.001:
                return timedelta(hours=mid)
            elif confidence > threshold:
                low = mid
            else:
                high = mid
        
        return timedelta(hours=high)


@dataclass
class DecayingBelief:
    """A belief with automatic confidence decay tracking."""
    
    content: str
    initial_confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    decay_engine: Optional[ConfidenceDecay] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_current_confidence(self, 
                               current_time: Optional[datetime] = None) -> float:
        """Get the current confidence value after decay."""
        engine = self.decay_engine or ConfidenceDecay()
        return engine.calculate_decay(
            self.initial_confidence,
            self.created_at,
            current_time
        )
    
    def refresh(self, new_confidence: Optional[float] = None) -> None:
        """Refresh the belief, optionally updating confidence."""
        self.last_accessed = datetime.now()
        if new_confidence is not None:
            self.initial_confidence = new_confidence
            self.created_at = datetime.now()
    
    def is_expired(self, threshold: float = 0.1) -> bool:
        """Check if belief confidence has fallen below threshold."""
        return self.get_current_confidence() < threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "initial_confidence": self.initial_confidence,
            "current_confidence": self.get_current_confidence(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "metadata": self.metadata
        }


class BeliefStore:
    """Store for managing decaying beliefs."""
    
    def __init__(self, decay_config: Optional[DecayConfig] = None):
        self._beliefs: Dict[str, DecayingBelief] = {}
        self.decay_engine = ConfidenceDecay(decay_config)
    
    def add_belief(self, content: str, confidence: float,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new belief to the store."""
        belief_id = f"bel_{hash(content) & 0xFFFFFFFF:08x}"
        
        belief = DecayingBelief(
            content=content,
            initial_confidence=confidence,
            decay_engine=self.decay_engine,
            metadata=metadata or {}
        )
        
        self._beliefs[belief_id] = belief
        return belief_id
    
    def get_belief(self, belief_id: str) -> Optional[DecayingBelief]:
        """Retrieve a belief by ID."""
        return self._beliefs.get(belief_id)
    
    def update_confidence(self, belief_id: str, new_confidence: float) -> bool:
        """Manually update a belief's confidence."""
        belief = self._beliefs.get(belief_id)
        if not belief:
            return False
        
        belief.refresh(new_confidence)
        return True
    
    def cleanup_expired(self, threshold: float = 0.1) -> List[str]:
        """Remove all expired beliefs and return their IDs."""
        expired_ids = [
            bid for bid, belief in self._beliefs.items()
            if belief.is_expired(threshold)
        ]
        
        for bid in expired_ids:
            del self._beliefs[bid]
        
        return expired_ids
    
    def get_all_active(self, min_confidence: float = 0.0) -> List[DecayingBelief]:
        """Get all beliefs above minimum confidence threshold."""
        return [
            belief for belief in self._beliefs.values()
            if belief.get_current_confidence() >= min_confidence
        ]
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the belief store."""
        confidences = [b.get_current_confidence() for b in self._beliefs.values()]
        
        return {
            "total_beliefs": len(self._beliefs),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0,
            "expired_count": sum(1 for c in confidences if c < 0.1)
        }


# Global instance
_belief_store: Optional[BeliefStore] = None


def get_belief_store(config: Optional[DecayConfig] = None) -> BeliefStore:
    """Get the global belief store instance."""
    global _belief_store
    if _belief_store is None:
        _belief_store = BeliefStore(decay_config=config)
    return _belief_store


if __name__ == "__main__":
    # Test decay functions
    config = DecayConfig(function=DecayFunction.EXPONENTIAL, half_life_hours=12)
    decay = ConfidenceDecay(config)
    
    initial = 0.95
    now = datetime.now()
    
    print(f"Initial confidence: {initial}")
    print(f"After 6 hours: {decay.calculate_decay(initial, now, now + timedelta(hours=6)):.3f}")
    print(f"After 12 hours: {decay.calculate_decay(initial, now, now + timedelta(hours=12)):.3f}")
    print(f"After 24 hours: {decay.calculate_decay(initial, now, now + timedelta(hours=24)):.3f}")
    
    # Test belief store
    store = get_belief_store(config)
    bel_id = store.add_belief("Python is great", 0.9)
    belief = store.get_belief(bel_id)
    
    if belief:
        print(f"\nBelief: {belief.content}")
        print(f"Current confidence: {belief.get_current_confidence():.3f}")
        print(f"Stats: {store.stats()}")
