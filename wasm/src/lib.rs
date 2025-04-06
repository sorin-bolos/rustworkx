use wasm_bindgen::prelude::*;
use web_sys::console;

// Import rustworkx-core for graph algorithms
use rustworkx_core::petgraph;
use rustworkx_core::petgraph::graph::{Graph, NodeIndex};
use rustworkx_core::petgraph::visit::{Dfs, NodeIndexable, IntoNodeIdentifiers};

#[wasm_bindgen(start)]
pub fn start() {
    console::log_1(&"rustworkx WebAssembly module initialized".into());
    console_error_panic_hook::set_once();
}

#[wasm_bindgen]
pub struct PyGraph {
    graph: Graph<JsValue, JsValue, petgraph::Undirected>,
}

#[wasm_bindgen]
impl PyGraph {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            graph: Graph::new_undirected(),
        }
    }

    pub fn add_node(&mut self, data: JsValue) -> usize {
        let idx = self.graph.add_node(data);
        idx.index()
    }

    pub fn add_edge(&mut self, source: usize, target: usize, data: JsValue) -> usize {
        let source_idx = NodeIndex::new(source);
        let target_idx = NodeIndex::new(target);
        let idx = self.graph.add_edge(source_idx, target_idx, data);
        idx.index()
    }

    pub fn node_count(&self) -> usize {
        self.graph.node_count()
    }

    pub fn edge_count(&self) -> usize {
        self.graph.edge_count()
    }
    
    pub fn is_connected(&self) -> bool {
        // If graph is empty or has only one node, it's connected
        if self.graph.node_count() <= 1 {
            return true;
        }
        
        // Get the first node as starting point
        let start_node = match self.graph.node_identifiers().next() {
            Some(node) => node,
            None => return true, // Empty graph is connected by definition
        };
        
        // Run DFS from the start node
        let mut dfs = Dfs::new(&self.graph, start_node);
        let mut visited_count = 0;
        
        while let Some(_) = dfs.next(&self.graph) {
            visited_count += 1;
        }
        
        // Graph is connected if DFS visited all nodes
        visited_count == self.graph.node_count()
    }
}

#[wasm_bindgen]
pub struct PyDiGraph {
    graph: Graph<JsValue, JsValue, petgraph::Directed>,
}

#[wasm_bindgen]
impl PyDiGraph {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            graph: Graph::new(),
        }
    }

    pub fn add_node(&mut self, data: JsValue) -> usize {
        let idx = self.graph.add_node(data);
        idx.index()
    }

    pub fn add_edge(&mut self, source: usize, target: usize, data: JsValue) -> usize {
        let source_idx = NodeIndex::new(source);
        let target_idx = NodeIndex::new(target);
        let idx = self.graph.add_edge(source_idx, target_idx, data);
        idx.index()
    }

    pub fn node_count(&self) -> usize {
        self.graph.node_count()
    }

    pub fn edge_count(&self) -> usize {
        self.graph.edge_count()
    }
}
