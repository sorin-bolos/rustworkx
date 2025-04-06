// WebAssembly entry point and initialization

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen(start)]
pub fn wasm_start() {
    // Initialize panic hook for better error messages
    std::panic::set_hook(Box::new(console_error_panic_hook::hook));
    
    // Log initialization message
    web_sys::console::log_1(&JsValue::from_str("rustworkx WebAssembly module initialized"));
}

// PyO3 WebAssembly initialization
#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn initialize_rustworkx_wasm() -> Result<(), JsValue> {
    // Any additional initialization specific to the Python environment
    Ok(())
}
