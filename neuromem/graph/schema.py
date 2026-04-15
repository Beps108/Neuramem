"""
NeuraMem Schema Module
Dataclasses and serialization for all data models.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import json


class EntityType(Enum):
    """Types of entities in NeuraMem."""
    BELIEF = "belief"
    MEMORY = "memory"
    AGENT = "agent"
    TRACE = "trace"
    CONTRADICTION = "contradiction"


@dataclass
class BaseSchema:
    """Base schema with common fields."""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseSchema':
        """Create from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at'] and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class BeliefSchema(BaseSchema):
    """Schema for belief entities."""
    content: str = ""
    confidence: float = 1.0
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    entity_type: EntityType = EntityType.BELIEF


@dataclass
class MemorySchema(BaseSchema):
    """Schema for memory entities."""
    content: str = ""
    memory_type: str = "episodic"
    confidence: float = 1.0
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    entity_type: EntityType = EntityType.MEMORY


@dataclass
class AgentSchema(BaseSchema):
    """Schema for agent entities."""
    name: str = ""
    parent_id: Optional[str] = None
    beliefs: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"
    entity_type: EntityType = EntityType.AGENT


@dataclass
class TraceSchema(BaseSchema):
    """Schema for reasoning trace entities."""
    initial_beliefs: List[str] = field(default_factory=list)
    conclusion: str = ""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    confidence: float = 1.0
    entity_type: EntityType = EntityType.TRACE


@dataclass
class ContradictionSchema(BaseSchema):
    """Schema for contradiction entities."""
    belief_ids: List[str] = field(default_factory=list)
    type: str = "direct"
    severity: str = "medium"
    description: str = ""
    resolved: bool = False
    entity_type: EntityType = EntityType.CONTRADICTION


class SchemaSerializer:
    """Utility for serializing/deserializing schemas."""
    
    @staticmethod
    def serialize(obj: BaseSchema) -> str:
        """Serialize a schema object to JSON."""
        return obj.to_json()
    
    @staticmethod
    def deserialize(data: str, schema_class: type) -> BaseSchema:
        """Deserialize JSON to a schema object."""
        dict_data = json.loads(data)
        return schema_class.from_dict(dict_data)
    
    @staticmethod
    def batch_serialize(objects: List[BaseSchema]) -> str:
        """Serialize multiple objects to JSON array."""
        return json.dumps([obj.to_dict() for obj in objects], indent=2)
    
    @staticmethod
    def batch_deserialize(data: str, schema_class: type) -> List[BaseSchema]:
        """Deserialize JSON array to list of schema objects."""
        dict_list = json.loads(data)
        return [schema_class.from_dict(d) for d in dict_list]


if __name__ == "__main__":
    # Test schemas
    belief = BeliefSchema(
        id="bel_001",
        content="The sky is blue",
        confidence=0.95,
        tags=["observation", "weather"]
    )
    
    print("Belief Schema:")
    print(belief.to_json())
    
    # Test serialization
    serialized = SchemaSerializer.serialize(belief)
    deserialized = SchemaSerializer.deserialize(serialized, BeliefSchema)
    print(f"\nDeserialized: {deserialized.content}")
