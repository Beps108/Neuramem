"""
NeuraMem Query Module
Named query functions for the hypergraph.
"""
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta


class GraphQueries:
    """Named query functions for graph operations."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def find_path(self, start_id: str, end_id: str, 
                 max_depth: int = 5) -> Optional[List[str]]:
        """Find a path between two nodes using BFS."""
        if start_id == end_id:
            return [start_id]
        
        visited = {start_id}
        queue = [(start_id, [start_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            neighbors = self.graph.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor == end_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_connected_component(self, node_id: str) -> Set[str]:
        """Get all nodes in the same connected component."""
        visited = set()
        stack = [node_id]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            neighbors = self.graph.get_neighbors(current)
            stack.extend(n for n in neighbors if n not in visited)
        
        return visited
    
    def find_common_connections(self, node_ids: List[str]) -> Set[str]:
        """Find nodes connected to all specified nodes."""
        if not node_ids:
            return set()
        
        common = self.graph.get_neighbors(node_ids[0])
        
        for nid in node_ids[1:]:
            common &= self.graph.get_neighbors(nid)
        
        return common
    
    def get_node_degree(self, node_id: str) -> int:
        """Get the degree (number of connections) of a node."""
        return len(self.graph.get_neighbors(node_id))
    
    def find_hubs(self, min_degree: int = 3) -> List[Dict[str, Any]]:
        """Find hub nodes with high connectivity."""
        hubs = []
        
        for node_id in self.graph._nodes:
            degree = self.get_node_degree(node_id)
            if degree >= min_degree:
                node = self.graph.get_node(node_id)
                hubs.append({
                    "node_id": node_id,
                    "label": node.label if node else "unknown",
                    "degree": degree
                })
        
        return sorted(hubs, key=lambda x: x["degree"], reverse=True)
    
    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        """Extract a subgraph containing specified nodes and their edges."""
        node_set = set(node_ids)
        subgraph_nodes = []
        subgraph_edges = []
        
        for nid in node_ids:
            node = self.graph.get_node(nid)
            if node:
                subgraph_nodes.append(node.to_dict())
        
        for edge in self.graph._edges.values():
            if any(nid in node_set for nid in edge.source_nodes + edge.target_nodes):
                subgraph_edges.append(edge.to_dict())
        
        return {
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "node_count": len(subgraph_nodes),
            "edge_count": len(subgraph_edges)
        }


# Global query instance
_queries_cache: Dict[str, GraphQueries] = {}


def get_queries(graph) -> GraphQueries:
    """Get or create query instance for a graph."""
    graph_id = id(graph)
    if graph_id not in _queries_cache:
        _queries_cache[graph_id] = GraphQueries(graph)
    return _queries_cache[graph_id]


if __name__ == "__main__":
    from neuromem.graph.hypergraph import get_hypergraph
    
    graph = get_hypergraph()
    queries = get_queries(graph)
    
    # Create test graph
    n1 = graph.add_node("Person", {"name": "Alice"})
    n2 = graph.add_node("Person", {"name": "Bob"})
    n3 = graph.add_node("Person", {"name": "Carol"})
    n4 = graph.add_node("Project", {"name": "ProjectX"})
    
    graph.add_edge("KNOWS", [n1], [n2, n3])
    graph.add_edge("WORKS_ON", [n1, n2], [n4])
    
    # Test queries
    print(f"Path Alice to Carol: {queries.find_path(n1, n3)}")
    print(f"Connected component: {queries.get_connected_component(n1)}")
    print(f"Hubs: {queries.find_hubs(min_degree=1)}")
