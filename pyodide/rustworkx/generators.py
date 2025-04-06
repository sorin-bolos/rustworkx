"""
Graph generators for rustworkx WebAssembly.
"""

from .wrapper import PyGraph, PyDiGraph

def path_graph(n, bidirectional=False):
    """
    Generate a path graph with n nodes.
    
    Args:
        n (int): Number of nodes
        bidirectional (bool): If True, create a directed graph with edges in both directions
            
    Returns:
        PyGraph or PyDiGraph: A path graph with n nodes
    """
    if bidirectional:
        g = PyDiGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n-1):
            g.add_edge(i, i+1, None)
            g.add_edge(i+1, i, None)
        
        return g
    else:
        g = PyGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n-1):
            g.add_edge(i, i+1, None)
        
        return g

def cycle_graph(n, bidirectional=False):
    """
    Generate a cycle graph with n nodes.
    
    Args:
        n (int): Number of nodes
        bidirectional (bool): If True, create a directed graph with edges in both directions
            
    Returns:
        PyGraph or PyDiGraph: A cycle graph with n nodes
    """
    if n < 3:
        raise ValueError("Cycle graph must have at least 3 nodes")
    
    if bidirectional:
        g = PyDiGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n-1):
            g.add_edge(i, i+1, None)
            g.add_edge(i+1, i, None)
        
        # Add edges to close the cycle
        g.add_edge(n-1, 0, None)
        g.add_edge(0, n-1, None)
        
        return g
    else:
        g = PyGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n-1):
            g.add_edge(i, i+1, None)
        
        # Add edge to close the cycle
        g.add_edge(n-1, 0, None)
        
        return g

def complete_graph(n, bidirectional=False):
    """
    Generate a complete graph with n nodes.
    
    Args:
        n (int): Number of nodes
        bidirectional (bool): If True, create a directed graph with edges in both directions
            
    Returns:
        PyGraph or PyDiGraph: A complete graph with n nodes
    """
    if bidirectional:
        g = PyDiGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    g.add_edge(i, j, None)
        
        return g
    else:
        g = PyGraph()
        nodes = g.add_nodes_from([None] * n)
        
        for i in range(n):
            for j in range(i+1, n):
                g.add_edge(i, j, None)
        
        return g
