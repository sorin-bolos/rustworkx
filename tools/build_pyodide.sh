#!/bin/bash
# Build rustworkx for Pyodide/WebAssembly

set -e

# Ensure Rust is installed and wasm32 target is available
rustup target add wasm32-unknown-emscripten

# Set environment variable to indicate Pyodide build
export PYODIDE=1

# Install emscripten if not already installed
if ! command -v emcc &> /dev/null; then
    echo "Installing emscripten..."
    git clone https://github.com/emscripten-core/emsdk.git
    cd emsdk
    ./emsdk install latest
    ./emsdk activate latest
    source ./emsdk_env.sh
    cd ..
fi

# Build the package with Pyodide settings
pip install -U setuptools wheel setuptools-rust
python setup.py bdist_wheel

echo "Build complete. Wheel file is in the dist/ directory."