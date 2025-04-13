#!/bin/bash
set -e

# Simple script to check WASM compilation
rustup target add --toolchain nightly wasm32-unknown-emscripten

# Verify syntax only
cargo +nightly check --target wasm32-unknown-emscripten --features wasm

echo "Syntax check successful"
