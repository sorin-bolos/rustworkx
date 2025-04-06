#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import argparse
import tempfile
from setuptools import setup, find_packages

SCRIPT_DIR = Path(__file__).parent.absolute()

def parse_args():
    parser = argparse.ArgumentParser(description="Build rustworkx for WebAssembly")
    parser.add_argument("--docker", action="store_true", help="Use Docker for building")
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

def build_wasm_package(use_docker=False):
    """Build the WebAssembly package."""
    print("Building WebAssembly package...")
    
    # Create build directory
    build_dir = SCRIPT_DIR / "build" / "wasm"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)
    
    if use_docker:
        print("Building with Docker...")
        # Use Docker to build the WebAssembly package
        subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{SCRIPT_DIR}:/src",
            "-w", "/src/wasm",  # Changed to wasm subdirectory
            "emscripten/emsdk",
            "bash", "-c", "wasm-pack build --target web --out-dir ../build/wasm"
        ], check=True)
    else:
        # Build the wasm package locally
        env = os.environ.copy()
        env["RUSTFLAGS"] = "--cfg=web_sys_unstable_apis"
        
        print("Building with wasm-pack...")
        # Point to the wasm directory
        wasm_dir = SCRIPT_DIR / "wasm"
        subprocess.run([
            "wasm-pack", "build",
            "--target", "web",
            "--out-dir", str(build_dir),
            str(wasm_dir)
        ], check=True, env=env)
    
    # After wasm-pack build completes successfully
    wasm_dir = Path("build") / "wasm"
    
    # Create a proper Python wheel package
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Create package structure
        pkg_dir = temp_path / "rustworkx"
        pkg_dir.mkdir()
        
        # Copy files to package directory
        wasm_file = wasm_dir / "rustworkx_wasm_bg.wasm"
        js_file = wasm_dir / "rustworkx_wasm.js"
        
        # Create __init__.py that imports the WASM module
        with open(pkg_dir / "__init__.py", "w") as f:
            f.write("""
# Rustworkx WebAssembly package
from js import document, rustworkx_wasm

# Import classes from the wasm module
from .wrapper import PyGraph, PyDiGraph

__version__ = "0.17.0"
""")
            
        # Create wrapper module for the wasm bindings
        with open(pkg_dir / "wrapper.py", "w") as f:
            f.write("""
# Wrapper classes for rustworkx WebAssembly bindings
from js import rustworkx_wasm

class PyGraph:
    def __init__(self):
        self._graph = rustworkx_wasm.PyGraph.new()
    
    def add_node(self, data):
        return self._graph.add_node(data)
    
    def add_edge(self, source, target, data):
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
    
    def add_edge(self, source, target, data):
        return self._graph.add_edge(source, target, data)
    
    def node_count(self):
        return self._graph.node_count()
    
    def edge_count(self):
        return self._graph.edge_count()
""")
                
        # Copy wasm files
        shutil.copy(wasm_file, pkg_dir)
        shutil.copy(js_file, pkg_dir)
        
        # Create setup.py
        with open(temp_path / "setup.py", "w") as f:
            f.write("""
from setuptools import setup, find_packages

setup(
    name="rustworkx",
    version="0.17.0",
    description="Python bindings for the rustworkx graph library (WebAssembly version)",
    packages=find_packages(),
    package_data={
        "rustworkx": ["*.wasm", "*.js"],
    },
    python_requires=">=3.7",
)
""")
        
        # Create MANIFEST.in to include non-python files
        with open(temp_path / "MANIFEST.in", "w") as f:
            f.write("""
include rustworkx/*.wasm
include rustworkx/*.js
""")
        
        # Build wheel
        print("Building wheel package...")
        wheel_cmd = [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(Path("build") / "pyodide"), temp_path]
        subprocess.run(wheel_cmd, check=True)
        
        # Create pyodide directory and copy necessary files
        pyodide_dir = Path("build") / "pyodide"
        pyodide_dir.mkdir(exist_ok=True)
        
        # Copy the necessary files for regular loading in pyodide
        # The wheel file already contains everything, but these are kept for compatibility
        meta_json = {
            "name": "rustworkx",
            "version": "0.17.0"
        }
        with open(pyodide_dir / "meta.json", "w") as f:
            json.dump(meta_json, f)
            
        # Copy the __init__.py for direct loading
        shutil.copy(pkg_dir / "__init__.py", pyodide_dir / "__init__.py")
        
        print(f"Wheel package created at {pyodide_dir}")
    
    return wasm_dir

def main():
    """Main build function."""
    args = parse_args()
    
    if not args.docker:
        setup_wasm_environment()
    
    wasm_build_dir = build_wasm_package(args.docker)
    
    # Create pyodide package
    pyodide_build_dir = Path("build") / "pyodide"
    pyodide_build_dir.mkdir(exist_ok=True)
    
    print("WebAssembly build complete!")
    print(f"WASM build output: {wasm_build_dir}")
    print(f"Pyodide package: {pyodide_build_dir}")
    print("\nTo use with Pyodide:")
    print("1. Copy the contents of the pyodide directory to your Pyodide distribution")
    print("2. Load it with `micropip.install(\"./path/to/rustworkx-0.17.0-py3-none-any.whl\")`")

if __name__ == "__main__":
    main()
