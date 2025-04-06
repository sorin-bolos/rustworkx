//! WebAssembly compatibility layer for rustworkx-core

pub mod parallel {
    #[cfg(not(target_arch = "wasm32"))]
    pub use rayon::prelude::*;
    #[cfg(not(target_arch = "wasm32"))]
    pub use rayon::slice::ParallelSliceMut;
    #[cfg(not(target_arch = "wasm32"))]
    pub use rayon_cond::CondIterator;

    #[cfg(target_arch = "wasm32")]
    pub struct CondIterator<I> {
        iter: I,
    }

    #[cfg(target_arch = "wasm32")]
    impl<I, T> CondIterator<I>
    where
        I: Iterator<Item = T>,
    {
        pub fn new<J: IntoIterator<IntoIter = I, Item = T>>(iter: J, _use_parallel: bool) -> Self {
            Self {
                iter: iter.into_iter(),
            }
        }
    }

    #[cfg(target_arch = "wasm32")]
    impl<I, T> Iterator for CondIterator<I>
    where
        I: Iterator<Item = T>,
    {
        type Item = T;

        fn next(&mut self) -> Option<Self::Item> {
            self.iter.next()
        }
    }

    // Create sequential versions of parallel slice methods for WASM
    #[cfg(target_arch = "wasm32")]
    pub trait ParallelSliceMut<T> {
        fn par_sort(&mut self)
        where
            T: Ord;
        fn par_sort_by<F>(&mut self, compare: F)
        where
            F: FnMut(&T, &T) -> std::cmp::Ordering;
        fn par_sort_by_key<B, F>(&mut self, f: F)
        where
            B: Ord,
            F: FnMut(&T) -> B;
        fn par_sort_unstable(&mut self)
        where
            T: Ord;
        fn par_sort_unstable_by<F>(&mut self, compare: F)
        where
            F: FnMut(&T, &T) -> std::cmp::Ordering;
        fn par_sort_unstable_by_key<B, F>(&mut self, f: F)
        where
            B: Ord,
            F: FnMut(&T) -> B;
    }

    #[cfg(target_arch = "wasm32")]
    impl<T> ParallelSliceMut<T> for [T] {
        fn par_sort(&mut self)
        where
            T: Ord,
        {
            self.sort();
        }

        fn par_sort_by<F>(&mut self, compare: F)
        where
            F: FnMut(&T, &T) -> std::cmp::Ordering,
        {
            self.sort_by(compare);
        }

        fn par_sort_by_key<B, F>(&mut self, f: F)
        where
            B: Ord,
            F: FnMut(&T) -> B,
        {
            self.sort_by_key(f);
        }

        fn par_sort_unstable(&mut self)
        where
            T: Ord,
        {
            self.sort_unstable();
        }

        fn par_sort_unstable_by<F>(&mut self, compare: F)
        where
            F: FnMut(&T, &T) -> std::cmp::Ordering,
        {
            self.sort_unstable_by(compare);
        }

        fn par_sort_unstable_by_key<B, F>(&mut self, f: F)
        where
            B: Ord,
            F: FnMut(&T) -> B,
        {
            self.sort_unstable_by_key(f);
        }
    }

    #[cfg(target_arch = "wasm32")]
    pub trait IntoParallelIterator {
        type Item;
        type Iter: Iterator<Item = Self::Item>;

        fn into_par_iter(self) -> Self::Iter;
    }

    #[cfg(target_arch = "wasm32")]
    impl<T> IntoParallelIterator for Vec<T> {
        type Item = T;
        type Iter = std::vec::IntoIter<T>;

        fn into_par_iter(self) -> Self::Iter {
            self.into_iter()
        }
    }
}

#[cfg(target_arch = "wasm32")]
pub use self::parallel::*;

// Logging utilities that work in both environments
pub fn log_info(message: &str) {
    #[cfg(target_arch = "wasm32")]
    {
        use wasm_bindgen::prelude::*;
        web_sys::console::log_1(&JsValue::from_str(message));
    }
    
    #[cfg(not(target_arch = "wasm32"))]
    {
        println!("INFO: {}", message);
    }
}

// Thread-local context with fallback for WebAssembly
pub struct ThreadContext<T> {
    #[cfg(not(target_arch = "wasm32"))]
    thread_local: std::cell::RefCell<T>,
    
    #[cfg(target_arch = "wasm32")]
    global: std::cell::RefCell<T>,
}

impl<T: Default> ThreadContext<T> {
    pub fn new() -> Self {
        #[cfg(not(target_arch = "wasm32"))]
        {
            ThreadContext {
                thread_local: std::cell::RefCell::new(T::default()),
            }
        }
        
        #[cfg(target_arch = "wasm32")]
        {
            ThreadContext {
                global: std::cell::RefCell::new(T::default()),
            }
        }
    }
    
    pub fn with<F, R>(&self, f: F) -> R
    where
        F: FnOnce(&mut T) -> R,
    {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let mut value = self.thread_local.borrow_mut();
            f(&mut value)
        }
        
        #[cfg(target_arch = "wasm32")]
        {
            let mut value = self.global.borrow_mut();
            f(&mut value)
        }
    }
}
