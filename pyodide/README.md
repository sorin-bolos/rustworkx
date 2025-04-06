# RustworkX for Pyodide

This is the WebAssembly version of RustworkX, a Python graph library implemented in Rust.

## Usage with Pyodide

To use rustworkx in a Pyodide environment:

1. Load the JavaScript glue code and WebAssembly binary:

```html
<script type="module">
  import init, { PyGraph, PyDiGraph } from "./rustworkx_wasm.js";
  
  async function loadRustworkxWasm() {
    // Initialize the WASM module
    const wasm = await init();
    
    // Register it with Pyodide
    pyodide.registerJsModule("rustworkx_wasm", { PyGraph, PyDiGraph });
  }
  
  // Call this before importing rustworkx in Python
  await loadRustworkxWasm();
  
  // Now you can use it in Python
  await pyodide.runPythonAsync(`
    import rustworkx as rx
    
    # Create a graph
    g = rx.PyGraph()
    n1 = g.add_node("Node 1")
    n2 = g.add_node("Node 2")
    g.add_edge(n1, n2, "Edge 1-2")
    
    print(f"Graph has {g.node_count()} nodes and {g.edge_count()} edges")
  `);
</script>
```

2. Alternatively, install the wheel package:

```python
import micropip
await micropip.install('./rustworkx-0.17.0-py3-none-any.whl')
import rustworkx as rx
```

## Current Limitations

The WebAssembly version currently supports a subset of the full rustworkx API.
