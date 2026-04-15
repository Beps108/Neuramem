"""
NeuraMem Hypergraph Module
Kuzu-backed hypergraph engine for complex relationship modeling.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime
import hashlib


@dataclass
class Node:
    """A node in the hypergraph."""
    
    node_id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class HyperEdge:
    """A hyperedge connecting multiple nodes."""
    
    edge_id: str
    label: str
    source_nodes: List[str]
    target_nodes: List[str]
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "label": self.label,
            "source_nodes": self.source_nodes,
            "target_nodes": self.target_nodes,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }


class HyperGraph:
    """Hypergraph storage and query engine."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, HyperEdge] = {}
        self._node_index: Dict[str, Set[str]] = {}
        self._edge_index: Dict[str, Set[str]] = {}
    
    def add_node(self, label: str, properties: Optional[Dict[str, Any]] = None) -> str:
        """Add a node to the graph."""
        node_id = f"n_{hashlib.sha256(f'{label}{datetime.now()}'.encode()).hexdigest()[:12]}"
        
        node = Node(
            node_id=node_id,
            label=label,
            properties=properties or {}
        )
        
        self._nodes[node_id] = node
        
        # Index by label
        if label not in self._node_index:
            self._node_index[label] = set()
        self._node_index[label].add(node_id)
        
        return node_id
    
    def add_edge(self, label: str, source_ids: List[str], 
                target_ids: List[str],
                properties: Optional[Dict[str, Any]] = None) -> str:
        """Add a hyperedge to the graph."""
        edge_id = f"e_{hashlib.sha256(f'{label}{datetime.now()}'.encode()).hexdigest()[:12]}"
        
        edge = HyperEdge(
            edge_id=edge_id,
            label=label,
            source_nodes=source_ids,
            target_nodes=target_ids,
            properties=properties or {}
        )
        
        self._edges[edge_id] = edge
        
        # Index by label
        if label not in self._edge_index:
            self._edge_index[label] = set()
        self._edge_index[label].add(edge_id)
        
        return edge_id
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self._nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[HyperEdge]:
        """Get an edge by ID."""
        return self._edges.get(edge_id)
    
    def find_nodes(self, label: Optional[str] = None,
                  properties: Optional[Dict[str, Any]] = None) -> List[Node]:
        """Find nodes by label and/or properties."""
        results = []
        
        if label:
            node_ids = self._node_index.get(label, set())
            candidates = [self._nodes[nid] for nid in node_ids if nid in self._nodes]
        else:
            candidates = list(self._nodes.values())
        
        if properties:
            for node in candidates:
                if all(node.properties.get(k) == v for k, v in properties.items()):
                    results.append(node)
        else:
            results = candidates
        
        return results
    
    def find_edges(self, label: Optional[str] = None,
                  connected_to: Optional[List[str]] = None) -> List[HyperEdge]:
        """Find edges by label and/or connected nodes."""
        results = []
        
        if label:
            edge_ids = self._edge_index.get(label, set())
            candidates = [self._edges[eid] for eid in edge_ids if eid in self._edges]
        else:
            candidates = list(self._edges.values())
        
        if connected_to:
            connected_set = set(connected_to)
            for edge in candidates:
                all_nodes = set(edge.source_nodes + edge.target_nodes)
                if all_nodes & connected_set:
                    results.append(edge)
        else:
            results = candidates
        
        return results
    
    def get_neighbors(self, node_id: str, direction: str = "both") -> Set[str]:
        """Get neighboring node IDs."""
        neighbors = set()
        
        for edge in self._edges.values():
            if node_id in edge.source_nodes:
                if direction in ["out", "both"]:
                    neighbors.update(edge.target_nodes)
            if node_id in edge.target_nodes:
                if direction in ["in", "both"]:
                    neighbors.update(edge.source_nodes)
        
        neighbors.discard(node_id)
        return neighbors
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its incident edges."""
        if node_id not in self._nodes:
            return False
        
        # Remove incident edges
        edges_to_remove = [
            eid for eid, edge in self._edges.items()
            if node_id in edge.source_nodes or node_id in edge.target_nodes
        ]
        
        for eid in edges_to_remove:
            del self._edges[eid]
        
        # Remove from index
        node = self._nodes[node_id]
        if node.label in self._node_index:
            self._node_index[node.label].discard(node_id)
        
        del self._nodes[node_id]
        return True
    
    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "node_labels": len(self._node_index),
            "edge_labels": len(self._edge_index),
            "avg_degree": sum(len(self.get_neighbors(nid)) for nid in self._nodes) / len(self._nodes) if self._nodes else 0
        }


# Global instance
_hypergraph: Optional[HyperGraph] = None


def get_hypergraph(db_path: Optional[str] = None) -> HyperGraph:
    """Get the global hypergraph instance."""
    global _hypergraph
    if _hypergraph is None:
        _hypergraph = HyperGraph(db_path=db_path)
    return _hypergraph


if __name__ == "__main__":
    graph = get_hypergraph()
    
    # Add nodes
    n1 = graph.add_node("Person", {"name": "Alice", "age": 30})
    n2 = graph.add_node("Person", {"name": "Bob", "age": 25})
    n3 = graph.add_node("Project", {"name": "NeuraMem"})
    
    # Add hyperedge (multiple sources to multiple targets)
    graph.add_edge("COLLABORATES_ON", [n1, n2], [n3])
    
    print(f"Graph stats: {graph.stats()}")
    print(f"Alice's neighbors: {graph.get_neighbors(n1)}")
