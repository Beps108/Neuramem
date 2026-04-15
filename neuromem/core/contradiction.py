"""
NeuraMem Contradiction Detection Module (Feature 3)
Detects and manages contradictions between beliefs and memories.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime
from enum import Enum
import hashlib
import re


class ContradictionType(Enum):
    """Types of contradictions that can be detected."""
    DIRECT = "direct"  # A vs not-A
    IMPLICIT = "implicit"  # A implies B, but we have not-B
    TEMPORAL = "temporal"  # Conflicting information at same time
    QUANTITATIVE = "quantitative"  # Conflicting numeric values
    CATEGORICAL = "categorical"  # Mutually exclusive categories


class ContradictionSeverity(Enum):
    """Severity levels for detected contradictions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Contradiction:
    """Represents a detected contradiction between beliefs."""
    
    belief_id_1: str
    belief_id_2: str
    contradiction_type: ContradictionType
    severity: ContradictionSeverity
    description: str
    confidence: float
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def get_id(self) -> str:
        """Generate unique ID for this contradiction."""
        content = f"{self.belief_id_1}:{self.belief_id_2}:{self.contradiction_type.value}"
        return f"con_{hashlib.sha256(content.encode()).hexdigest()[:12]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.get_id(),
            "belief_id_1": self.belief_id_1,
            "belief_id_2": self.belief_id_2,
            "contradiction_type": self.contradiction_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "confidence": self.confidence,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes
        }


class ContradictionDetector:
    """Detects contradictions between beliefs using various strategies."""
    
    def __init__(self):
        self._negation_patterns = [
            (r"\bnot\s+(\w+)", r"\1"),
            (r"\bisn't\s+(\w+)", r"\1"),
            (r"\baren't\s+(\w+)", r"\1"),
            (r"\bdoesn't\s+(\w+)", r"\1"),
            (r"\bdon't\s+(\w+)", r"\1"),
            (r"\bnever\s+(\w+)", r"\1"),
            (r"(\w+)\s+is\s+false", r"\1"),
            (r"it\s+is\s+not\s+true\s+that\s+(.+)", r"\1"),
        ]
        
        self._mutually_exclusive = {
            "true": {"false"},
            "false": {"true"},
            "alive": {"dead"},
            "dead": {"alive"},
            "hot": {"cold"},
            "cold": {"hot"},
            "big": {"small"},
            "small": {"big"},
            "yes": {"no"},
            "no": {"yes"},
            "exists": {"not_exists"},
            "present": {"absent"},
            "absent": {"present"},
        }
    
    def extract_claims(self, text: str) -> List[str]:
        """Extract individual claims from text."""
        sentences = re.split(r'[.!?]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def normalize_claim(self, claim: str) -> str:
        """Normalize a claim for comparison."""
        normalized = claim.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def get_negation(self, claim: str) -> Optional[str]:
        """Get the negated form of a claim if pattern matches."""
        normalized = self.normalize_claim(claim)
        
        for pattern, replacement in self._negation_patterns:
            match = re.search(pattern, normalized)
            if match:
                return re.sub(pattern, replacement, normalized)
        
        return None
    
    def is_negation(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are negations of each other."""
        norm1 = self.normalize_claim(claim1)
        norm2 = self.normalize_claim(claim2)
        
        if norm1 == norm2:
            return False
        
        neg1 = self.get_negation(claim1)
        neg2 = self.get_negation(claim2)
        
        return (neg1 and norm2 == neg1) or (neg2 and norm1 == neg2)
    
    def has_mutually_exclusive_terms(self, claim1: str, claim2: str) -> Optional[Tuple[str, str]]:
        """Check if claims contain mutually exclusive terms."""
        norm1 = set(self.normalize_claim(claim1).split())
        norm2 = set(self.normalize_claim(claim2).split())
        
        for term1 in norm1:
            if term1 in self._mutually_exclusive:
                exclusives = self._mutually_exclusive[term1]
                for term2 in norm2:
                    if term2 in exclusives:
                        return (term1, term2)
        
        return None
    
    def detect_direct_contradiction(self, claim1: str, claim2: str) -> bool:
        """Detect direct contradictions (A vs not-A)."""
        return self.is_negation(claim1, claim2)
    
    def detect_categorical_contradiction(self, claim1: str, claim2: str) -> bool:
        """Detect contradictions via mutually exclusive categories."""
        return self.has_mutually_exclusive_terms(claim1, claim2) is not None
    
    def detect_quantitative_contradiction(self, value1: Any, value2: Any, 
                                         tolerance: float = 0.0) -> bool:
        """Detect contradictions in numeric values."""
        try:
            num1 = float(value1)
            num2 = float(value2)
            
            if tolerance > 0:
                return abs(num1 - num2) > tolerance
            else:
                return num1 != num2
        except (ValueError, TypeError):
            return False
    
    def calculate_severity(self, contradiction_type: ContradictionType,
                          confidence1: float, confidence2: float) -> ContradictionSeverity:
        """Calculate severity based on type and confidence levels."""
        avg_confidence = (confidence1 + confidence2) / 2
        
        if contradiction_type == ContradictionType.DIRECT:
            if avg_confidence > 0.9:
                return ContradictionSeverity.CRITICAL
            elif avg_confidence > 0.7:
                return ContradictionSeverity.HIGH
            elif avg_confidence > 0.5:
                return ContradictionSeverity.MEDIUM
            else:
                return ContradictionSeverity.LOW
        
        elif contradiction_type == ContradictionType.CATEGORICAL:
            if avg_confidence > 0.8:
                return ContradictionSeverity.HIGH
            elif avg_confidence > 0.6:
                return ContradictionSeverity.MEDIUM
            else:
                return ContradictionSeverity.LOW
        
        else:
            if avg_confidence > 0.7:
                return ContradictionSeverity.MEDIUM
            else:
                return ContradictionSeverity.LOW


class ContradictionStore:
    """Manages storage and retrieval of detected contradictions."""
    
    def __init__(self):
        self._contradictions: Dict[str, Contradiction] = {}
        self._by_belief: Dict[str, Set[str]] = {}
        self._unresolved: Set[str] = set()
        self.detector = ContradictionDetector()
    
    def add_contradiction(self, contradiction: Contradiction) -> str:
        """Add a contradiction to the store."""
        con_id = contradiction.get_id()
        
        if con_id in self._contradictions:
            return con_id
        
        self._contradictions[con_id] = contradiction
        
        # Index by beliefs involved
        for bel_id in [contradiction.belief_id_1, contradiction.belief_id_2]:
            if bel_id not in self._by_belief:
                self._by_belief[bel_id] = set()
            self._by_belief[bel_id].add(con_id)
        
        if not contradiction.resolved:
            self._unresolved.add(con_id)
        
        return con_id
    
    def check_and_record(self, belief_id_1: str, content1: str, conf1: float,
                        belief_id_2: str, content2: str, conf2: float) -> Optional[Contradiction]:
        """Check for contradiction between two beliefs and record if found."""
        contradiction = self.detect(belief_id_1, content1, conf1,
                                   belief_id_2, content2, conf2)
        
        if contradiction:
            self.add_contradiction(contradiction)
        
        return contradiction
    
    def detect(self, belief_id_1: str, content1: str, conf1: float,
              belief_id_2: str, content2: str, conf2: float) -> Optional[Contradiction]:
        """Detect contradiction between two beliefs."""
        # Check direct contradiction
        if self.detector.detect_direct_contradiction(content1, content2):
            severity = self.detector.calculate_severity(
                ContradictionType.DIRECT, conf1, conf2
            )
            return Contradiction(
                belief_id_1=belief_id_1,
                belief_id_2=belief_id_2,
                contradiction_type=ContradictionType.DIRECT,
                severity=severity,
                description=f"Direct contradiction: '{content1}' vs '{content2}'",
                confidence=max(conf1, conf2)
            )
        
        # Check categorical contradiction
        result = self.detector.detect_categorical_contradiction(content1, content2)
        if result:
            term1, term2 = result
            severity = self.detector.calculate_severity(
                ContradictionType.CATEGORICAL, conf1, conf2
            )
            return Contradiction(
                belief_id_1=belief_id_1,
                belief_id_2=belief_id_2,
                contradiction_type=ContradictionType.CATEGORICAL,
                severity=severity,
                description=f"Categorical contradiction: '{term1}' vs '{term2}'",
                confidence=max(conf1, conf2)
            )
        
        return None
    
    def get_by_belief(self, belief_id: str) -> List[Contradiction]:
        """Get all contradictions involving a specific belief."""
        con_ids = self._by_belief.get(belief_id, set())
        return [self._contradictions[cid] for cid in con_ids if cid in self._contradictions]
    
    def get_unresolved(self) -> List[Contradiction]:
        """Get all unresolved contradictions."""
        return [self._contradictions[cid] for cid in self._unresolved if cid in self._contradictions]
    
    def resolve(self, contradiction_id: str, notes: Optional[str] = None) -> bool:
        """Mark a contradiction as resolved."""
        if contradiction_id not in self._contradictions:
            return False
        
        contradiction = self._contradictions[contradiction_id]
        contradiction.resolved = True
        contradiction.resolution_notes = notes
        
        self._unresolved.discard(contradiction_id)
        return True
    
    def count(self) -> int:
        """Get total contradiction count."""
        return len(self._contradictions)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about contradictions."""
        by_type = {}
        by_severity = {}
        
        for con in self._contradictions.values():
            ctype = con.contradiction_type.value
            csev = con.severity.value
            
            by_type[ctype] = by_type.get(ctype, 0) + 1
            by_severity[csev] = by_severity.get(csev, 0) + 1
        
        return {
            "total": self.count(),
            "unresolved": len(self._unresolved),
            "resolved": self.count() - len(self._unresolved),
            "by_type": by_type,
            "by_severity": by_severity
        }


# Global instance
_contradiction_store: Optional[ContradictionStore] = None


def get_contradiction_store() -> ContradictionStore:
    """Get the global contradiction store instance."""
    global _contradiction_store
    if _contradiction_store is None:
        _contradiction_store = ContradictionStore()
    return _contradiction_store


if __name__ == "__main__":
    store = get_contradiction_store()
    
    # Test contradiction detection
    con = store.check_and_record(
        "bel_001", "The light is on", 0.95,
        "bel_002", "The light is not on", 0.90
    )
    
    if con:
        print(f"Contradiction detected: {con.description}")
        print(f"Type: {con.contradiction_type.value}")
        print(f"Severity: {con.severity.value}")
    
    # Test categorical
    con2 = store.check_and_record(
        "bel_003", "The patient is alive", 0.85,
        "bel_004", "The patient is dead", 0.80
    )
    
    if con2:
        print(f"\nCategorical contradiction: {con2.description}")
    
    print(f"\nStats: {store.stats()}")
