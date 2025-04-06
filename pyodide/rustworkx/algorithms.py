"""
Algorithms for the rustworkx WebAssembly package
"""

def is_connected(graph):
    """
    Check if the graph is connected.
    
    Args:
        graph: A PyGraph object
        
    Returns:
        bool: True if the graph is connected, False otherwise
    """
    return graph.is_connected()

def number_of_nodes(graph):
    """
    Return the number of nodes in the graph.
    
    Args:
        graph: A PyGraph or PyDiGraph object
        
    Returns:
        int: The number of nodes
    """
    return graph.node_count()

def number_of_edges(graph):
    """
    Return the number of edges in the graph.
    
    Args:
        graph: A PyGraph or PyDiGraph object
        
    Returns:
        int: The number of edges
    """
    return graph.edge_count()

def is_empty(graph):
    """
    Check if the graph is empty (has no nodes).
    
    Args:
        graph: A PyGraph or PyDiGraph object
        
    Returns:
        bool: True if the graph is empty, False otherwise
    """
    return graph.node_count() == 0
