"""
NeuraMem Reasoning Trace Module (Feature 4)
Tracks and stores reasoning chains and inference paths.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum
import hashlib
import json


class InferenceType(Enum):
    """Types of logical inference."""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    PROBABILISTIC = "probabilistic"


class TraceStatus(Enum):
    """Status of a reasoning trace."""
    ACTIVE = "active"
    COMPLETED = "completed"
    INVALIDATED = "invalidated"
    PARTIAL = "partial"


@dataclass
class InferenceStep:
    """A single step in a reasoning chain."""
    
    step_id: str
    operation: str
    inputs: List[str]
    output: str
    confidence: float
    inference_type: InferenceType
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "operation": self.operation,
            "inputs": self.inputs,
            "output": self.output,
            "confidence": self.confidence,
            "inference_type": self.inference_type.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ReasoningTrace:
    """Complete reasoning trace from premise to conclusion."""
    
    trace_id: str
    initial_beliefs: List[str]
    final_conclusion: str
    steps: List[InferenceStep]
    status: TraceStatus
    overall_confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: InferenceStep) -> None:
        """Add a step to the reasoning chain."""
        self.steps.append(step)
        
        # Update overall confidence (multiplicative)
        self.overall_confidence *= step.confidence
    
    def get_chain(self) -> List[str]:
        """Get the full reasoning chain as text."""
        chain = ["Initial beliefs:"]
        for belief in self.initial_beliefs:
            chain.append(f"  - {belief}")
        
        chain.append("\nReasoning steps:")
        for i, step in enumerate(self.steps, 1):
            chain.append(f"  {i}. [{step.inference_type.value}] {step.operation}")
            chain.append(f"     Input: {', '.join(step.inputs)}")
            chain.append(f"     Output: {step.output}")
            chain.append(f"     Confidence: {step.confidence:.2f}")
        
        chain.append(f"\nConclusion: {self.final_conclusion}")
        chain.append(f"Overall confidence: {self.overall_confidence:.2f}")
        
        return chain
    
    def complete(self, conclusion: str) -> None:
        """Mark the trace as completed with a final conclusion."""
        self.final_conclusion = conclusion
        self.status = TraceStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def invalidate(self, reason: str) -> None:
        """Invalidate the trace."""
        self.status = TraceStatus.INVALIDATED
        self.metadata["invalidation_reason"] = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "initial_beliefs": self.initial_beliefs,
            "final_conclusion": self.final_conclusion,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value,
            "overall_confidence": self.overall_confidence,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "metadata": self.metadata
        }


class ReasoningTracer:
    """Manages creation and tracking of reasoning traces."""
    
    def __init__(self):
        self._traces: Dict[str, ReasoningTrace] = {}
        self._by_belief: Dict[str, Set[str]] = {}
        self._active_traces: Set[str] = set()
    
    def create_trace(self, initial_beliefs: List[str], 
                    tags: Optional[List[str]] = None) -> ReasoningTrace:
        """Create a new reasoning trace."""
        trace_id = f"trace_{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:12]}"
        
        trace = ReasoningTrace(
            trace_id=trace_id,
            initial_beliefs=initial_beliefs,
            final_conclusion="",
            steps=[],
            status=TraceStatus.ACTIVE,
            overall_confidence=1.0,
            tags=tags or []
        )
        
        self._traces[trace_id] = trace
        self._active_traces.add(trace_id)
        
        # Index by initial beliefs
        for belief in initial_beliefs:
            if belief not in self._by_belief:
                self._by_belief[belief] = set()
            self._by_belief[belief].add(trace_id)
        
        return trace
    
    def add_step(self, trace_id: str, operation: str, inputs: List[str],
                output: str, confidence: float,
                inference_type: InferenceType,
                metadata: Optional[Dict[str, Any]] = None) -> Optional[InferenceStep]:
        """Add a step to an existing trace."""
        trace = self._traces.get(trace_id)
        if not trace or trace.status != TraceStatus.ACTIVE:
            return None
        
        step_id = f"step_{len(trace.steps)}_{hashlib.sha256(output.encode()).hexdigest()[:8]}"
        
        step = InferenceStep(
            step_id=step_id,
            operation=operation,
            inputs=inputs,
            output=output,
            confidence=confidence,
            inference_type=inference_type,
            metadata=metadata or {}
        )
        
        trace.add_step(step)
        return step
    
    def complete_trace(self, trace_id: str, conclusion: str) -> bool:
        """Complete a trace with a final conclusion."""
        trace = self._traces.get(trace_id)
        if not trace or trace.status != TraceStatus.ACTIVE:
            return False
        
        trace.complete(conclusion)
        self._active_traces.discard(trace_id)
        return True
    
    def get_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Retrieve a trace by ID."""
        return self._traces.get(trace_id)
    
    def get_traces_by_belief(self, belief: str) -> List[ReasoningTrace]:
        """Get all traces that used a specific belief."""
        trace_ids = self._by_belief.get(belief, set())
        return [self._traces[tid] for tid in trace_ids if tid in self._traces]
    
    def get_active_traces(self) -> List[ReasoningTrace]:
        """Get all currently active traces."""
        return [self._traces[tid] for tid in self._active_traces if tid in self._traces]
    
    def export_trace(self, trace_id: str, format: str = "json") -> str:
        """Export a trace in specified format."""
        trace = self._traces.get(trace_id)
        if not trace:
            return ""
        
        if format == "json":
            return json.dumps(trace.to_dict(), indent=2)
        elif format == "text":
            return "\n".join(trace.get_chain())
        else:
            return json.dumps(trace.to_dict())
    
    def count(self) -> int:
        """Get total trace count."""
        return len(self._traces)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about reasoning traces."""
        by_status = {}
        by_type = {}
        confidences = []
        
        for trace in self._traces.values():
            status = trace.status.value
            by_status[status] = by_status.get(status, 0) + 1
            confidences.append(trace.overall_confidence)
            
            for step in trace.steps:
                itype = step.inference_type.value
                by_type[itype] = by_type.get(itype, 0) + 1
        
        return {
            "total_traces": self.count(),
            "active": len(self._active_traces),
            "by_status": by_status,
            "by_inference_type": by_type,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0
        }


# Global instance
_reasoning_tracer: Optional[ReasoningTracer] = None


def get_reasoning_tracer() -> ReasoningTracer:
    """Get the global reasoning tracer instance."""
    global _reasoning_tracer
    if _reasoning_tracer is None:
        _reasoning_tracer = ReasoningTracer()
    return _reasoning_tracer


if __name__ == "__main__":
    tracer = get_reasoning_tracer()
    
    # Create a sample reasoning trace
    trace = tracer.create_trace(
        initial_beliefs=[
            "All humans are mortal",
            "Socrates is human"
        ],
        tags=["logic", "syllogism"]
    )
    
    # Add reasoning steps
    tracer.add_step(
        trace_id=trace.trace_id,
        operation="universal_instantiation",
        inputs=["All humans are mortal", "Socrates is human"],
        output="If Socrates is human, then Socrates is mortal",
        confidence=0.99,
        inference_type=InferenceType.DEDUCTIVE
    )
    
    tracer.add_step(
        trace_id=trace.trace_id,
        operation="modus_ponens",
        inputs=["Socrates is human", "If Socrates is human, then Socrates is mortal"],
        output="Socrates is mortal",
        confidence=0.98,
        inference_type=InferenceType.DEDUCTIVE
    )
    
    # Complete the trace
    tracer.complete_trace(trace.trace_id, "Socrates is mortal")
    
    # Print results
    print("Reasoning Chain:")
    print("\n".join(trace.get_chain()))
    print(f"\nStats: {tracer.stats()}")
