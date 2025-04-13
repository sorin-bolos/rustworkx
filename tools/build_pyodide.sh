#!/bin/bash
# Build rustworkx for Pyodide/WebAssembly

set -e

# Install and set nightly Rust toolchain for Emscripten support
echo "Installing nightly Rust toolchain for Emscripten support..."
rustup toolchain install nightly
rustup override set nightly
rustup target add --toolchain nightly wasm32-unknown-emscripten

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
else
    echo "Emscripten already installed."
    emcc --version
fi

# Try using the correct pyodide command
if command -v pyodide &> /dev/null; then
    echo "Building with pyodide build tool..."
    pyodide build
else
    echo "pyodide build tools not available, falling back to setuptools..."
    # Build the package with standard setuptools
    pip install -U setuptools wheel setuptools-rust
    python setup.py bdist_wheel
fi

# Restore default Rust toolchain after build is complete
echo "Restoring default Rust toolchain..."
rustup override unset

echo "Build complete. Wheel file is in the dist/ directory."