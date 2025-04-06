// Web utilities for the Python module in WebAssembly environment

use pyo3::prelude::*;

#[pymodule]
pub fn web_utils(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add any web-specific functionality here
    
    #[cfg(target_arch = "wasm32")]
    {
        #[pyfn(m)]
        fn is_wasm_environment(_py: Python) -> PyResult<bool> {
            Ok(true)
        }
        
        #[pyfn(m)]
        fn get_browser_info(_py: Python) -> PyResult<String> {
            use wasm_bindgen::JsCast;
            let window = web_sys::window().expect("should have a window in this context");
            let navigator = window.navigator();
            let user_agent = navigator.user_agent().unwrap_or_else(|_| "Unknown".into());
            Ok(user_agent)
        }
    }
    
    #[cfg(not(target_arch = "wasm32"))]
    {
        #[pyfn(m)]
        fn is_wasm_environment(_py: Python) -> PyResult<bool> {
            Ok(false)
        }
        
        #[pyfn(m)]
        fn get_browser_info(_py: Python) -> PyResult<String> {
            Ok("Not running in a browser".to_string())
        }
    }
    
    Ok(())
}
