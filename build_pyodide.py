#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import json
import argparse
from pathlib import Path
import tempfile

SCRIPT_DIR = Path(__file__).parent.absolute()

def parse_args():
    parser = argparse.ArgumentParser(description="Build rustworkx for Pyodide")
    parser.add_argument("--release", action="store_true", help="Build in release mode", default=True)
    parser.add_argument("--debug", action="store_false", dest="release", help="Build in debug mode")
    parser.add_argument("--output-dir", type=str, help="Output directory for wheel file",
                      default=str(SCRIPT_DIR / "build" / "pyodide"))
    return parser.parse_args()

def setup_wasm_environment():
    """Setup the build environment for WebAssembly compilation."""
    print("Setting up WebAssembly build environment...")
    
    # Check if wasm-pack is installed
    try:
        subprocess.run(["wasm-pack", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing wasm-pack...")
        subprocess.run(["cargo", "install", "wasm-pack"], check=True)
    
    # Check if Rust has the wasm32 target
    try:
        output = subprocess.run(
            ["rustup", "target", "list", "--installed"],
            check=True,
            capture_output=True,
            text=True
        ).stdout
        if "wasm32-unknown-unknown" not in output:
            print("Adding wasm32-unknown-unknown target...")
            subprocess.run(["rustup", "target", "add", "wasm32-unknown-unknown"], check=True)
    except subprocess.CalledProcessError:
        print("Error checking Rust targets. Please ensure rustup is installed.")
        sys.exit(1)

def build_wasm_package(release=True):
    """Build the WebAssembly package using wasm-pack."""
    print("Building WebAssembly package...")
    
    # Create build directory
    build_dir = SCRIPT_DIR / "build" / "wasm"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Build the wasm package
    env = os.environ.copy()
    env["RUSTFLAGS"] = "--cfg=web_sys_unstable_apis"
    
    print(f"Building with wasm-pack in {'release' if release else 'debug'} mode...")
    
    # Point to the wasm directory
    wasm_dir = SCRIPT_DIR / "wasm"
    subprocess.run([
        "wasm-pack", "build",
        "--target", "web",
        "--out-dir", str(build_dir),
        "--" + ("release" if release else "dev"),
        str(wasm_dir)
    ], check=True, env=env)
    
    return build_dir

def copy_wasm_to_package(wasm_build_dir, package_dir):
    """Copy the WASM files to the Python package directory."""
    print("Copying WASM files to Python package...")
    
    # Create the package directory if it doesn't exist
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the WASM binary and JS glue code
    shutil.copy(wasm_build_dir / "rustworkx_wasm_bg.wasm", package_dir / "rustworkx_wasm.wasm")
    shutil.copy(wasm_build_dir / "rustworkx_wasm.js", package_dir / "rustworkx_wasm.js")
    
    print(f"WASM files copied to {package_dir}")

def build_wheel(pyodide_dir, output_dir):
    """Build the Python wheel package."""
    print("Building Python wheel package...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Build the wheel using pip
    subprocess.run([
        sys.executable, "-m", "pip", "wheel",
        "--no-deps",
        "-w", str(output_path),
        str(pyodide_dir)
    ], check=True)
    
    print(f"Wheel package built in {output_path}")
    return output_path

def create_wheel_loader_html(output_dir):
    """Create an HTML file for testing the wheel."""
    html_path = Path(output_dir) / "test_rustworkx_wheel.html"
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Rustworkx Wheel Test in Pyodide</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
</head>
<body>
    <h2>Testing Rustworkx Wheel in Pyodide</h2>
    <div id="output" style="white-space: pre-wrap; font-family: monospace;"></div>
    
    <script type="text/javascript">
        async function main() {
            const output = document.getElementById("output");
            output.textContent = "Loading Pyodide...\\n";
            
            // Load Pyodide
            const pyodide = await loadPyodide();
            output.textContent += "Pyodide loaded.\\n";
            
            try {
                // First load the wasm module
                output.textContent += "Loading WASM module...\\n";
                
                const rustworkx_wasm_mod = await import('./rustworkx_wasm.js');
                const rustworkx_wasm = await rustworkx_wasm_mod.default(
                    await fetch('./rustworkx_wasm.wasm').then(r => r.arrayBuffer())
                );
                
                // Register the module with Pyodide
                pyodide.registerJsModule("rustworkx_wasm", rustworkx_wasm);
                output.textContent += "Registered WASM module.\\n";
                
                // Install micropip
                await pyodide.loadPackage("micropip");
                output.textContent += "Installed micropip.\\n";
                
                // Find the wheel file
                const wheelFiles = await pyodide.runPythonAsync(`
                    import glob
                    glob.glob("*.whl")
                `);
                
                if (wheelFiles.length === 0) {
                    throw new Error("No wheel files found in current directory");
                }
                
                const wheelFile = wheelFiles[0];
                output.textContent += `Installing wheel from ${wheelFile}...\\n`;
                
                // Install the wheel
                await pyodide.runPythonAsync(`
                    import micropip
                    await micropip.install('${wheelFile}')
                `);
                
                // Test the package
                const result = await pyodide.runPythonAsync(`
                    import rustworkx as rx
                    
                    output = []
                    output.append(f"Rustworkx version: {rx.__version__}")
                    
                    # Create a simple graph
                    g = rx.PyGraph()
                    n1 = g.add_node("Node 1")
                    n2 = g.add_node("Node 2")
                    e = g.add_edge(n1, n2, "Edge 1-2")
                    
                    output.append(f"Created graph with {g.node_count()} nodes and {g.edge_count()} edge")
                    output.append(f"Graph is connected: {g.is_connected()}")
                    
                    # Create a directed graph
                    dg = rx.PyDiGraph()
                    n1 = dg.add_node("Node 1")
                    n2 = dg.add_node("Node 2")
                    n3 = dg.add_node("Node 3")
                    e1 = dg.add_edge(n1, n2, "Edge 1->2")
                    e2 = dg.add_edge(n2, n3, "Edge 2->3")
                    
                    output.append(f"DiGraph created with {dg.node_count()} nodes and {dg.edge_count()} edges")
                    
                    # Test generators
                    path = rx.path_graph(5)
                    output.append(f"Path graph has {path.node_count()} nodes and {path.edge_count()} edges")
                    
                    cycle = rx.cycle_graph(6)
                    output.append(f"Cycle graph has {cycle.node_count()} nodes and {cycle.edge_count()} edges")
                    
                    complete = rx.complete_graph(4)
                    output.append(f"Complete graph has {complete.node_count()} nodes and {complete.edge_count()} edges")
                    
                    "\\n".join(output)
                `);
                
                output.textContent += result;
                output.textContent += "\\n\\nTests completed successfully!";
            } catch (error) {
                output.textContent += "Error: " + error;
                console.error(error);
            }
        }
        
        main();
    </script>
</body>
</html>""")
    
    print(f"Test HTML file created at {html_path}")

def main():
    """Main build function."""
    args = parse_args()
    
    # Setup the WebAssembly environment
    setup_wasm_environment()
    
    # Build the WebAssembly package
    wasm_build_dir = build_wasm_package(release=args.release)
    
    # Copy the WASM files to the Python package
    pyodide_dir = SCRIPT_DIR / "pyodide"
    rustworkx_pkg_dir = pyodide_dir / "rustworkx"
    copy_wasm_to_package(wasm_build_dir, rustworkx_pkg_dir)
    
    # Build the wheel
    output_dir = args.output_dir
    wheel_dir = build_wheel(pyodide_dir, output_dir)
    
    # Copy JS and WASM files to the output dir for easier testing
    shutil.copy(wasm_build_dir / "rustworkx_wasm.js", Path(output_dir) / "rustworkx_wasm.js")
    shutil.copy(wasm_build_dir / "rustworkx_wasm_bg.wasm", Path(output_dir) / "rustworkx_wasm.wasm")
    
    # Create a test HTML file
    create_wheel_loader_html(output_dir)
    
    print("\nBuild completed successfully!")
    print(f"Output directory: {output_dir}")
    print("\nTo test with Pyodide:")
    print(f"1. Start a web server in the output directory: python -m http.server -d {output_dir} 8000")
    print("2. Open a browser and navigate to: http://localhost:8000/test_rustworkx_wheel.html")

if __name__ == "__main__":
    main()
