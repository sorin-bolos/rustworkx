# This file is part of the rustworkx Pyodide package
import numpy
from pyodide.ffi import create_proxy
from js import rustworkx_wasm

# Initialize the WebAssembly module
rustworkx_wasm.start()

# Define wrapper classes to match the Python API
class PyGraph:
    def __init__(self):
        self._graph = rustworkx_wasm.PyGraph.new()
    
    def add_node(self, data):
        return self._graph.add_node(data)
    
    def add_edge(self, source, target, data=None):
        return self._graph.add_edge(source, target, data)
    
    def node_count(self):
        return self._graph.node_count()
    
    def edge_count(self):
        return self._graph.edge_count()
    
    def is_connected(self):
        return self._graph.is_connected()

class PyDiGraph:
    def __init__(self):
        self._graph = rustworkx_wasm.PyDiGraph.new()
    
    def add_node(self, data):
        return self._graph.add_node(data)
    
    def add_edge(self, source, target, data=None):
        return self._graph.add_edge(source, target, data)
    
    def node_count(self):
        return self._graph.node_count()
    
    def edge_count(self):
        return self._graph.edge_count()
