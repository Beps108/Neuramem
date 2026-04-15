"""
NeuraMem Python SDK
Client library for interacting with NeuraMem API.
"""
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Belief:
    belief_id: str
    content: str
    confidence: float


class NeuraMemClient:
    """Python SDK client for NeuraMem API."""
    
    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def create_belief(self, content: str, confidence: float = 1.0) -> Belief:
        """Create a new belief."""
        response = self.session.post(
            f"{self.base_url}/api/v1/beliefs/",
            json={"content": content, "confidence": confidence}
        )
        response.raise_for_status()
        data = response.json()
        return Belief(
            belief_id=data["belief_id"],
            content=data["content"],
            confidence=data["confidence"]
        )
    
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Get a belief by ID."""
        response = self.session.get(f"{self.base_url}/api/v1/beliefs/{belief_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return Belief(
            belief_id=data["belief_id"],
            content=data["content"],
            confidence=data["confidence"]
        )
    
    def list_beliefs(self) -> List[Belief]:
        """List all beliefs."""
        response = self.session.get(f"{self.base_url}/api/v1/beliefs/")
        response.raise_for_status()
        return [Belief(**b) for b in response.json()]
    
    def reject_belief(self, content: str, reason: str = "contradiction") -> dict:
        """Reject a belief."""
        response = self.session.post(
            f"{self.base_url}/api/v1/rejections/",
            params={"content": content, "reason": reason}
        )
        response.raise_for_status()
        return response.json()
    
    def create_trace(self, initial_beliefs: List[str]) -> dict:
        """Create a reasoning trace."""
        response = self.session.post(
            f"{self.base_url}/api/v1/traces/",
            params={"initial_beliefs": initial_beliefs}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False


if __name__ == "__main__":
    client = NeuraMemClient()
    
    if client.health_check():
        print("Connected to NeuraMem API")
        
        belief = client.create_belief("Test belief", 0.9)
        print(f"Created belief: {belief.belief_id}")
    else:
        print("API not available")
