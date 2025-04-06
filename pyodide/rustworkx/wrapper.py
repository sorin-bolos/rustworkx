"""
Python wrapper classes for rustworkx WebAssembly bindings
"""

from js import rustworkx_wasm

class PyGraph:
    """
    Undirected graph class mirroring functionality of the native PyGraph.
    """
    def __init__(self):
        self._graph = rustworkx_wasm.PyGraph.new()
    
    def add_node(self, data):
        """Add a node to the graph with the specified data."""
        return self._graph.add_node(data)
    
    def add_nodes_from(self, nodes_list):
        """Add multiple nodes from an iterable."""
        return [self.add_node(data) for data in nodes_list]
    
    def add_edge(self, source, target, data):
        """Add an edge between source and target nodes with the specified data."""
        return self._graph.add_edge(source, target, data)
    
    def add_edges_from(self, edges_list):
        """Add multiple edges from an iterable of (source, target, data) tuples."""
        return [self.add_edge(source, target, data) for source, target, data in edges_list]
    
    def node_count(self):
        """Return the number of nodes in the graph."""
        return self._graph.node_count()
    
    def edge_count(self):
        """Return the number of edges in the graph."""
        return self._graph.edge_count()
    
    def is_connected(self):
        """Check if the graph is connected."""
        return self._graph.is_connected()
    
    def nodes(self):
        """Return a list of all node indices in the graph."""
        return list(range(self.node_count()))
    
    def edges(self):
        """Return a list of all edge indices in the graph."""
        return list(range(self.edge_count()))
    
    def __len__(self):
        """Return the number of nodes in the graph."""
        return self.node_count()
    
    def __contains__(self, node):
        """Check if a node index is in the graph."""
        return 0 <= node < self.node_count()
    
    def neighbors(self, node):
        """
        Return the neighbors of a node.
        
        Not implemented in WebAssembly version yet.
        """
        raise NotImplementedError("neighbors() not implemented in WebAssembly version yet")

class PyDiGraph:
    """
    Directed graph class mirroring functionality of the native PyDiGraph.
    """
    def __init__(self):
        self._graph = rustworkx_wasm.PyDiGraph.new()
    
    def add_node(self, data):
        """Add a node to the graph with the specified data."""
        return self._graph.add_node(data)
    
    def add_nodes_from(self, nodes_list):
        """Add multiple nodes from an iterable."""
        return [self.add_node(data) for data in nodes_list]
    
    def add_edge(self, source, target, data):
        """Add a directed edge from source to target with the specified data."""
        return self._graph.add_edge(source, target, data)
    
    def add_edges_from(self, edges_list):
        """Add multiple edges from an iterable of (source, target, data) tuples."""
        return [self.add_edge(source, target, data) for source, target, data in edges_list]
    
    def node_count(self):
        """Return the number of nodes in the graph."""
        return self._graph.node_count()
    
    def edge_count(self):
        """Return the number of edges in the graph."""
        return self._graph.edge_count()
    
    def nodes(self):
        """Return a list of all node indices in the graph."""
        return list(range(self.node_count()))
    
    def edges(self):
        """Return a list of all edge indices in the graph."""
        return list(range(self.edge_count()))
    
    def __len__(self):
        """Return the number of nodes in the graph."""
        return self.node_count()
    
    def __contains__(self, node):
        """Check if a node index is in the graph."""
        return 0 <= node < self.node_count()
    
    def predecessors(self, node):
        """
        Return the predecessors of a node.
        
        Not implemented in WebAssembly version yet.
        """
        raise NotImplementedError("predecessors() not implemented in WebAssembly version yet")
    
    def successors(self, node):
        """
        Return the successors of a node.
        
        Not implemented in WebAssembly version yet.
        """
        raise NotImplementedError("successors() not implemented in WebAssembly version yet")
    
    def is_directed_acyclic_graph(self):
        """
        Check if the graph is a directed acyclic graph (DAG).
        
        Not implemented in WebAssembly version yet.
        """
        raise NotImplementedError("is_directed_acyclic_graph() not implemented in WebAssembly version yet")
