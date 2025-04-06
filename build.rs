fn main() {
    // Prevent compiling Python bindings when targeting WebAssembly
    if std::env::var("TARGET").unwrap_or_default().contains("wasm32") {
        println!("cargo:rustc-cfg=target_arch=\"wasm32\"");
    }
}
