# Build rustworkx for Pyodide/WebAssembly

# Stop execution on error
$ErrorActionPreference = "Stop"

# Ensure Rust is installed and wasm32 target is available
rustup target add wasm32-unknown-emscripten

# Set environment variable to indicate Pyodide build
$env:PYODIDE = "1"

# Check if emscripten is installed
if (-not (Get-Command emcc -ErrorAction SilentlyContinue)) {
    Write-Host "Emscripten (emcc) not found. Installing it now..."
    
    # Clone the emsdk repo if it doesn't exist
    if (-not (Test-Path -Path "emsdk")) {
        git clone https://github.com/emscripten-core/emsdk.git
    }
    
    # Enter the emsdk directory and install
    Push-Location emsdk
    try {
        # Download and install the latest SDK
        & .\emsdk.ps1 install latest
        
        # Activate the latest SDK
        & .\emsdk.ps1 activate latest
        
        # Setup the environment variables for the current PowerShell session
        & .\emsdk_env.ps1
    } finally {
        Pop-Location
    }
    
    # Verify installation
    if (-not (Get-Command emcc -ErrorAction SilentlyContinue)) {
        Write-Host "Failed to install Emscripten automatically. Please install it manually."
        exit 1
    }
} else {
    Write-Host "Emscripten already installed."
    emcc --version
}

# Try to install and use pyodide-build
$pyodideBuildInstalled = $false
try {
    pip install pyodide-build
    $pyodideBuildInstalled = $true
} catch {
    Write-Host "Failed to install pyodide-build, will fall back to setuptools."
}

if ($pyodideBuildInstalled) {
    Write-Host "Building with pyodide-build tool..."
    pyodide-build build-wheel --target wasm32-unknown-emscripten
} else {
    Write-Host "pyodide-build not available, falling back to setuptools..."
    # Build the package with standard setuptools
    pip install -U setuptools wheel setuptools-rust
    python setup.py bdist_wheel
}

Write-Host "Build complete. Wheel file is in the dist/ directory."
