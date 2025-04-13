// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use petgraph::EdgeType;

use rand::prelude::*;

// Use different RNG implementations based on target
#[cfg(all(not(feature = "wasm"), not(target_os = "emscripten")))]
use rand_pcg::Pcg64;
#[cfg(any(feature = "wasm", target_os = "emscripten"))]
use rand::rngs::SmallRng;

use crate::iterators::Pos2DMapping;
use crate::StablePyGraph;

// Add a conditional implementation for the RNG creation
#[cfg(all(not(feature = "wasm"), not(target_os = "emscripten")))]
fn create_rng(seed: Option<u64>) -> impl rand::Rng {
    match seed {
        Some(seed_value) => Pcg64::seed_from_u64(seed_value),
        None => Pcg64::from_entropy(),
    }
}

#[cfg(any(feature = "wasm", target_os = "emscripten"))]
fn create_rng(seed: Option<u64>) -> impl rand::Rng {
    use rand::SeedableRng;
    match seed {
        Some(seed_value) => SmallRng::seed_from_u64(seed_value),
        None => SmallRng::from_entropy(),
    }
}

pub fn random_layout<Ty: EdgeType>(
    graph: &StablePyGraph<Ty>,
    center: Option<[f64; 2]>,
    seed: Option<u64>,
) -> Pos2DMapping {
    let mut rng = create_rng(seed);

    Pos2DMapping {
        pos_map: graph
            .node_indices()
            .map(|n| {
                let random_tuple: [f64; 2] = rng.gen();
                match center {
                    Some(center) => (
                        n.index(),
                        [random_tuple[0] + center[0], random_tuple[1] + center[1]],
                    ),
                    None => (n.index(), random_tuple),
                }
            })
            .collect(),
    }
}
