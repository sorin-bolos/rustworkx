"""
RustworkX WebAssembly Python Package
"""

__version__ = "0.17.0"

try:
    from js import rustworkx_wasm
    
    from .wrapper import PyGraph, PyDiGraph
    from .algorithms import (
        is_connected,
        number_of_nodes,
        number_of_edges,
        is_empty
    )
    from .generators import (
        path_graph,
        cycle_graph,
        complete_graph
    )
    
except ImportError as e:
    import sys
    print(f"Error: {e}", file=sys.stderr)
    print("The rustworkx_wasm JavaScript module must be loaded in the browser before importing rustworkx.", file=sys.stderr)
    print("Please ensure you've loaded and initialized the WASM module with:", file=sys.stderr)
    print("  pyodide.registerJsModule('rustworkx_wasm', rustworkx_wasm)", file=sys.stderr)
    
    # Define fallback stub classes for testing/development
    class PyGraph:
        def __init__(self):
            self.nodes = []
            self.edges = []
            print("WARNING: Using stub PyGraph implementation - WASM module not found")
        
        def add_node(self, data):
            self.nodes.append(data)
            return len(self.nodes) - 1
        
        def add_edge(self, source, target, data):
            self.edges.append((source, target, data))
            return len(self.edges) - 1
        
        def node_count(self):
            return len(self.nodes)
        
        def edge_count(self):
            return len(self.edges)
        
        def is_connected(self):
            return True

    class PyDiGraph(PyGraph):
        pass
    
    # Define stub functions
    def is_connected(graph):
        return True
    
    def number_of_nodes(graph):
        return graph.node_count()
    
    def number_of_edges(graph):
        return graph.edge_count()
    
    def is_empty(graph):
        return graph.node_count() == 0
    
    # Define stub generators
    def path_graph(n, bidirectional=False):
        if bidirectional:
            return PyDiGraph()
        return PyGraph()
    
    def cycle_graph(n, bidirectional=False):
        if bidirectional:
            return PyDiGraph()
        return PyGraph()
    
    def complete_graph(n, bidirectional=False):
        if bidirectional:
            return PyDiGraph()
        return PyGraph()
