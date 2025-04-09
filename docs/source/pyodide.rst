Pyodide / WebAssembly Support
==========================

Using rustworkx in web browsers
------------------------------

rustworkx can be used in web browsers through `Pyodide <https://pyodide.org/>`_, 
a Python distribution for the browser and WebAssembly/Wasm.

Installation
-----------

To use rustworkx in Pyodide, you can install it using the Pyodide package manager:

.. code-block:: javascript

    pyodide.loadPackage("rustworkx")

Then import it in Python code running in Pyodide:

.. code-block:: python

    import rustworkx as rx
    
    # Create a graph
    g = rx.PyGraph()
    a = g.add_node("A")
    b = g.add_node("B")
    c = g.add_node("C")
    g.add_edges_from([(a, b, 1.5), (a, c, 5.0), (b, c, 2.5)])
    
    # Use graph algorithms as normal
    path = rx.dijkstra_shortest_paths(g, a, c, weight_fn=float)

Limitations
----------

When using rustworkx in Pyodide, be aware of the following limitations:

1. **Performance**: While rustworkx in Pyodide is still faster than many pure Python 
   alternatives, WebAssembly performance may not match native performance.

2. **Memory Usage**: Browser environments typically have more limited memory compared to 
   desktop/server environments. Consider working with smaller graphs when possible.

3. **Threading**: Some parallel algorithms fall back to single-threaded implementations
   due to WebAssembly threading limitations.

Example
-------

Here's a complete example of using rustworkx in a web page with Pyodide:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>rustworkx with Pyodide Example</title>
        <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
    </head>
    <body>
        <div id="output"></div>
        <script type="text/javascript">
            async function main() {
                let pyodide = await loadPyodide();
                await pyodide.loadPackage("rustworkx");
                
                const output = document.getElementById("output");
                
                const result = await pyodide.runPythonAsync(`
                    import rustworkx as rx
                    
                    # Create a simple graph
                    g = rx.PyGraph()
                    a = g.add_node("A")
                    b = g.add_node("B")
                    c = g.add_node("C")
                    g.add_edges_from([(a, b, 1.5), (a, c, 5.0), (b, c, 2.5)])
                    
                    # Find shortest path
                    path = rx.dijkstra_shortest_paths(g, a, c, weight_fn=float)
                    f"Shortest path from A to C: {[g.nodes()[i] for i in path]}"
                `);
                
                output.textContent = result;
            }
            main();
        </script>
    </body>
    </html>