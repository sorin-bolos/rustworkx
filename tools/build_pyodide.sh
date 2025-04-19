#!/bin/bash
# Build rustworkx for Pyodide/WebAssembly

set -e

# Create a build log file for diagnostics
BUILD_LOG="rustworkx_pyodide_build.log"
echo "Starting build at $(date)" > $BUILD_LOG
echo "===== Environment Information =====" >> $BUILD_LOG

# Fix version extraction - get the actual version number correctly
get_emcc_version() {
    emcc --version | head -n 1 | sed -E 's/.*emcc .* ([0-9]+\.[0-9]+\.[0-9]+).*/\1/'
}

# Install and set stable Rust toolchain for Emscripten support since
# we're targeting Python 3.12 and Emscripten 3.1.58 which works with stable Rust
echo "Installing/updating stable Rust toolchain for Emscripten support..."
rustup toolchain install stable
rustup override set stable
rustup target add --toolchain stable wasm32-unknown-emscripten

# Set environment variable to indicate Pyodide build
export PYODIDE=1

# Install specific version of emscripten that's compatible with Pyodide
if ! command -v emcc &> /dev/null; then
    echo "Installing emscripten..."
    git clone https://github.com/emscripten-core/emsdk.git
    cd emsdk
    # Use version 3.1.58 as required by Pyodide
    ./emsdk install 3.1.58
    ./emsdk activate 3.1.58
    source ./emsdk_env.sh
    cd ..
else
    echo "Checking emscripten version..."
    current_version=$(get_emcc_version)
    echo "Current emscripten version: $current_version"
    # Enforce specific version
    if [[ "$current_version" != "3.1.58" ]]; then
        echo "ERROR: Current emscripten version ($current_version) is not compatible with Pyodide."
        echo "Installing and activating version 3.1.58 which is required..."
        
        # Check if emsdk is already installed
        if [ -d "emsdk" ]; then
            cd emsdk
        else
            git clone https://github.com/emscripten-core/emsdk.git
            cd emsdk
        fi
        
        ./emsdk install 3.1.58
        ./emsdk activate 3.1.58
        source ./emsdk_env.sh
        cd ..
        
        # Verify the version after installation
        current_version=$(get_emcc_version)
        echo "Now using emscripten version: $current_version"
    fi
fi

# Ensure we have the correct Emscripten version
current_version=$(get_emcc_version)
if [[ "$current_version" != "3.1.58" ]]; then
    echo "ERROR: Failed to set correct Emscripten version. Required: 3.1.58, Current: $current_version"
    echo "Please manually install Emscripten 3.1.58 before continuing."
    exit 1
fi

# Set environment variables needed for emscripten and PyO3
export EMCC_CFLAGS="-s ERROR_ON_UNDEFINED_SYMBOLS=0"

# IMPORTANT: Use appropriate flags for WebAssembly threading support
export RUSTFLAGS="-C target-feature=+atomics,+bulk-memory,+mutable-globals"
export CARGO_TARGET_WASM32_UNKNOWN_EMSCRIPTEN_LINKER=emcc

# Enable verbose cargo output for debugging
export CARGO_LOG=debug
export RUST_LOG=debug

# Set Python paths for cross-compilation
export PYTHON_SYS_EXECUTABLE="$(which python3)"
export PYO3_PYTHON="$(which python3)"

# For debugging and better error messages
export RUSTC_BOOTSTRAP=1
export RUST_BACKTRACE=1

# Add diagnostics to help troubleshoot build failures
echo "Rust version: $(rustc --version)"
echo "Emscripten version: $(emcc --version | head -n 1)"
echo "Python executable: $PYTHON_SYS_EXECUTABLE"
echo "Build environment ready, starting compilation..."

# Log environment details
{
  echo "Rust version: $(rustc --version)"
  echo "Emscripten version: $(emcc --version | head -n 1)"
  echo "Emscripten actual version: $(get_emcc_version)"
  echo "Python executable: $PYTHON_SYS_EXECUTABLE"
  echo "Python version: $($PYTHON_SYS_EXECUTABLE --version)"
  echo "RUSTFLAGS: $RUSTFLAGS"
  echo "EMCC_CFLAGS: $EMCC_CFLAGS"
  echo ""
  echo "===== Dependency Versions ====="
  echo "PyO3: $(grep 'version =' Cargo.toml | grep pyo3 | head -1 | awk -F'"' '{print $2}')"
  echo ""
  echo "===== Starting Build ====="
} >> $BUILD_LOG

# Try using the correct pyodide command
if command -v pyodide &> /dev/null; then
    echo "Building with pyodide build tool..."
    pyodide build 2>&1 | tee -a $BUILD_LOG
else
    echo "pyodide build tools not available, falling back to setuptools..."
    # Build the package with standard setuptools
    pip install -U setuptools wheel setuptools-rust
    
    # First run cargo directly to see detailed feature resolution
    echo "Running cargo check to debug feature resolution..."
    # No need for +nightly or -Z build-std flags with stable rust
    RUSTFLAGS="$RUSTFLAGS" cargo check --target wasm32-unknown-emscripten --features wasm -vv 2>&1 | tee -a $BUILD_LOG
    
    echo "Building wheel..."
    # For the actual build, use stable without special flags
    RUSTFLAGS="$RUSTFLAGS" python setup.py build_rust --release --plat-name=wasm32-unknown-emscripten --manylinux=off bdist_wheel 2>&1 | tee -a $BUILD_LOG
    fi

# Record build result
BUILD_RESULT=$?
echo "===== Build completed with status $BUILD_RESULT =====" >> $BUILD_LOG
if [ $BUILD_RESULT -eq 0 ]; then
    echo "Build succeeded" >> $BUILD_LOG
else
    echo "Build failed" >> $BUILD_LOG
fi

# Restore default Rust toolchain after build is complete
echo "Restoring default Rust toolchain..."
rustup override unset

echo "Build complete. Wheel file is in the dist/ directory."
echo "Build log saved to $BUILD_LOG"