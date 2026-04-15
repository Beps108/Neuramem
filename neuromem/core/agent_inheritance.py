"""
NeuraMem Agent Inheritance Module (Feature 5)
Manages belief inheritance and propagation between agents.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum
import hashlib


class InheritanceMode(Enum):
    """Modes of belief inheritance between agents."""
    FULL = "full"  # Inherit all beliefs
    SELECTIVE = "selective"  # Inherit based on rules
    FILTERED = "filtered"  # Inherit with filters applied
    WEIGHTED = "weighted"  # Inherit with confidence weighting


class AgentRelation(Enum):
    """Types of relationships between agents."""
    PARENT_CHILD = "parent_child"
    PEER = "peer"
    SUBORDINATE = "subordinate"
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"


@dataclass
class Belief:
    """A belief held by an agent."""
    
    belief_id: str
    content: str
    confidence: float
    source: Optional[str] = None
    inherited_from: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "belief_id": self.belief_id,
            "content": self.content,
            "confidence": self.confidence,
            "source": self.source,
            "inherited_from": self.inherited_from,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Agent:
    """An autonomous agent that holds beliefs."""
    
    agent_id: str
    name: str
    beliefs: Dict[str, Belief] = field(default_factory=dict)
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    relations: Dict[str, AgentRelation] = field(default_factory=dict)
    inheritance_mode: InheritanceMode = InheritanceMode.SELECTIVE
    inheritance_rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_belief(self, content: str, confidence: float,
                  source: Optional[str] = None,
                  inherited_from: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a belief to this agent."""
        belief_id = f"bel_{hashlib.sha256(content.encode()).hexdigest()[:12]}"
        
        belief = Belief(
            belief_id=belief_id,
            content=content,
            confidence=confidence,
            source=source or self.agent_id,
            inherited_from=inherited_from,
            metadata=metadata or {}
        )
        
        self.beliefs[belief_id] = belief
        return belief_id
    
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Retrieve a belief by ID."""
        return self.beliefs.get(belief_id)
    
    def remove_belief(self, belief_id: str) -> bool:
        """Remove a belief from this agent."""
        if belief_id in self.beliefs:
            del self.beliefs[belief_id]
            return True
        return False
    
    def add_child(self, child_id: str) -> None:
        """Add a child agent."""
        if child_id not in self.children:
            self.children.append(child_id)
    
    def set_relation(self, other_agent_id: str, relation: AgentRelation) -> None:
        """Set relationship with another agent."""
        self.relations[other_agent_id] = relation
    
    def count_beliefs(self) -> int:
        """Get total belief count."""
        return len(self.beliefs)


class AgentNetwork:
    """Manages a network of agents and belief inheritance."""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._inheritance_log: List[Dict[str, Any]] = []
    
    def create_agent(self, name: str, 
                    parent_id: Optional[str] = None,
                    inheritance_mode: InheritanceMode = InheritanceMode.SELECTIVE) -> Agent:
        """Create a new agent in the network."""
        agent_id = f"agent_{hashlib.sha256(f'{name}{datetime.now()}'.encode()).hexdigest()[:12]}"
        
        agent = Agent(
            agent_id=agent_id,
            name=name,
            parent_id=parent_id,
            inheritance_mode=inheritance_mode
        )
        
        self._agents[agent_id] = agent
        
        # Link to parent if exists
        if parent_id and parent_id in self._agents:
            parent = self._agents[parent_id]
            parent.add_child(agent_id)
            agent.set_relation(parent_id, AgentRelation.PARENT_CHILD)
            parent.set_relation(agent_id, AgentRelation.PARENT_CHILD)
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self._agents.get(agent_id)
    
    def inherit_beliefs(self, source_agent_id: str, target_agent_id: str,
                       filter_fn: Optional[callable] = None) -> List[str]:
        """Inherit beliefs from source to target agent."""
        source = self._agents.get(source_agent_id)
        target = self._agents.get(target_agent_id)
        
        if not source or not target:
            return []
        
        inherited_ids = []
        
        for belief_id, belief in source.beliefs.items():
            # Apply filter if provided
            if filter_fn and not filter_fn(belief):
                continue
            
            # Apply inheritance mode rules
            if target.inheritance_mode == InheritanceMode.FILTERED:
                if not self._passes_filters(belief, target.inheritance_rules):
                    continue
            
            # Calculate inherited confidence
            if target.inheritance_mode == InheritanceMode.WEIGHTED:
                inherited_confidence = belief.confidence * 0.9  # Decay on inheritance
            else:
                inherited_confidence = belief.confidence
            
            # Add inherited belief
            new_id = target.add_belief(
                content=belief.content,
                confidence=inherited_confidence,
                source=source_agent_id,
                inherited_from=belief_id,
                metadata={"original_confidence": belief.confidence}
            )
            
            inherited_ids.append(new_id)
        
        # Log inheritance
        self._inheritance_log.append({
            "timestamp": datetime.now().isoformat(),
            "source": source_agent_id,
            "target": target_agent_id,
            "count": len(inherited_ids),
            "mode": target.inheritance_mode.value
        })
        
        return inherited_ids
    
    def _passes_filters(self, belief: Belief, rules: List[Dict[str, Any]]) -> bool:
        """Check if belief passes inheritance filters."""
        for rule in rules:
            rule_type = rule.get("type")
            
            if rule_type == "min_confidence":
                if belief.confidence < rule.get("threshold", 0):
                    return False
            
            elif rule_type == "keyword_include":
                keywords = rule.get("keywords", [])
                if not any(kw.lower() in belief.content.lower() for kw in keywords):
                    return False
            
            elif rule_type == "keyword_exclude":
                keywords = rule.get("keywords", [])
                if any(kw.lower() in belief.content.lower() for kw in keywords):
                    return False
        
        return True
    
    def propagate_belief(self, belief_id: str, source_agent_id: str,
                        max_depth: int = 3) -> Dict[str, List[str]]:
        """Propagate a belief through the agent network."""
        propagated = {}
        visited = set()
        
        def _propagate(agent_id: str, depth: int):
            if depth > max_depth or agent_id in visited:
                return
            
            visited.add(agent_id)
            agent = self._agents.get(agent_id)
            if not agent:
                return
            
            # Propagate to children
            for child_id in agent.children:
                child = self._agents.get(child_id)
                if child and belief_id in agent.beliefs:
                    original_belief = agent.beliefs[belief_id]
                    
                    inherited_ids = self.inherit_beliefs(
                        agent_id, child_id,
                        filter_fn=lambda b: b.belief_id == belief_id
                    )
                    
                    if inherited_ids:
                        propagated[child_id] = inherited_ids
                        _propagate(child_id, depth + 1)
        
        _propagate(source_agent_id, 0)
        return propagated
    
    def get_ancestors(self, agent_id: str) -> List[str]:
        """Get all ancestor agents."""
        ancestors = []
        current = self._agents.get(agent_id)
        
        while current and current.parent_id:
            ancestors.append(current.parent_id)
            current = self._agents.get(current.parent_id)
        
        return ancestors
    
    def get_descendants(self, agent_id: str) -> List[str]:
        """Get all descendant agents."""
        descendants = []
        agent = self._agents.get(agent_id)
        if not agent:
            return descendants
        
        def _collect_children(a_id: str):
            a = self._agents.get(a_id)
            if not a:
                return
            for child_id in a.children:
                descendants.append(child_id)
                _collect_children(child_id)
        
        _collect_children(agent_id)
        return descendants
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the agent network."""
        total_beliefs = sum(a.count_beliefs() for a in self._agents.values())
        
        return {
            "total_agents": len(self._agents),
            "total_beliefs": total_beliefs,
            "avg_beliefs_per_agent": total_beliefs / len(self._agents) if self._agents else 0,
            "inheritance_events": len(self._inheritance_log),
            "root_agents": len([a for a in self._agents.values() if not a.parent_id]),
            "leaf_agents": len([a for a in self._agents.values() if not a.children])
        }


# Global instance
_agent_network: Optional[AgentNetwork] = None


def get_agent_network() -> AgentNetwork:
    """Get the global agent network instance."""
    global _agent_network
    if _agent_network is None:
        _agent_network = AgentNetwork()
    return _agent_network


if __name__ == "__main__":
    network = get_agent_network()
    
    # Create agent hierarchy
    parent = network.create_agent("Parent Agent", inheritance_mode=InheritanceMode.FULL)
    child1 = network.create_agent("Child 1", parent_id=parent.agent_id)
    child2 = network.create_agent("Child 2", parent_id=parent.agent_id)
    
    # Add beliefs to parent
    parent.add_belief("The sky is blue", 0.95)
    parent.add_belief("Water boils at 100C", 0.98)
    parent.add_belief("Unverified claim", 0.3)
    
    # Set up filtering for child1
    child1.inheritance_mode = InheritanceMode.FILTERED
    child1.inheritance_rules = [
        {"type": "min_confidence", "threshold": 0.5}
    ]
    
    # Inherit beliefs
    inherited = network.inherit_beliefs(parent.agent_id, child1.agent_id)
    print(f"Child 1 inherited {len(inherited)} beliefs")
    
    inherited2 = network.inherit_beliefs(parent.agent_id, child2.agent_id)
    print(f"Child 2 inherited {len(inherited2)} beliefs")
    
    # Show results
    print(f"\nChild 1 beliefs:")
    for bid, belief in child1.beliefs.items():
        print(f"  - {belief.content} (confidence: {belief.confidence:.2f})")
    
    print(f"\nNetwork stats: {network.stats()}")
