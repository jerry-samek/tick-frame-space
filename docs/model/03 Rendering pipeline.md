+---------------------------+       +--------------------------+       +--------------------------+
| 0. Input & initialization | ----> | 1. Salience propagation  | ----> | 2. Feature detection     |
| - Params (γ, α0, sources) |       | - ψ_t+1 = F(ψ_t; γ, α0)  |       | - Local maxima (clusters)|
| - Grid/lattice ψ(x, t=0)  |       | - Damping, diffusion     |       | - Gradients, radii, S    |
+---------------------------+       +--------------------------+       +--------------------------+
                                                                          |
                                                                          v
                                                        +----------------------------------+
                                                        | 3. Unit tracking & stability     |
                                                        | - Persistence (age, σ)           |
                                                        | - Drift Δx, variance Var(S)      |
                                                        | - Registry of units/composites   |
                                                        +----------------------------------+
                                                                          |
                                                                          v
+---------------------------+       +--------------------------+       +--------------------------+
| 4. Interactions           | ----> | 5. Event synthesis       | ----> | 6. Horizon-aware culling |
| - Binding (d_bind, g_min) |       | - unit_detected          |       | - Causal cone filter     |
| - Decay (σc < b_min)      |       | - composite_formed/decay |       | - Exclude superluminal   |
| - Nonlinear responses     |       | - translation/anomaly    |       |   or beyond-horizon data |
+---------------------------+       +--------------------------+       +--------------------------+
                                                                          |
                                                                          v
+---------------------------+       +--------------------------+       +--------------------------+
| 7. LOD & instancing       | ----> | 8. Stream & visualize    | ----> | 9. Audit & storage       |
| - Group similar units     |       | - SSE/WebSocket events   |       | - Snapshots every N ticks|
| - Detail by SPBI (LOD)    |       | - Color by σ, size by S  |       | - Reproducible logs      |
| - Suppress low-salience   |       | - Trails for drift       |       | - Deterministic seeds    |
+---------------------------+       +--------------------------+       +--------------------------+