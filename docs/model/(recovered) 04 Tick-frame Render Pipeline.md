# Tick-frame Render Pipeline

## 🎯 Overview
This document maps GPU rendering concepts to the tick-frame substrate as a staged pipeline.  
It shows how salience propagates, clusters form, events are emitted, and the observer sees only what’s inside the causal cone (horizon-aware culling).

---

## 🧪 Pipeline Stages

```text
+---------------------------+       +--------------------------+       +--------------------------+
| 0. Input & initialization | ----> | 1. Salience propagation  | ----> | 2. Feature detection     |
| - Params (γ, α₀, sources) |       | - ψₜ₊₁ = F(ψₜ; γ, α₀)     |       | - Local maxima (clusters)|
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
🎮 GPU Analogies
GPU Technique	Tick‑Frame Analog	Commentary
Instancing	Repeating salience clusters (e.g. proto‑atoms)	Clusters with similar salience profiles behave like instanced geometry — minimal variation, high reuse.
Level of Detail (LOD)	SPBI-driven salience granularity	High-SPBI zones show fine structure; low-SPBI zones collapse to coarse aggregates — like LOD switching.
Frustum Culling	Horizon boundary exclusion	Observer can’t see beyond causal cone — salience outside horizon is culled from view.
Occlusion Culling	Salience shadowing	Dense clusters can mask weaker ones; propagation blocked by high-salience zones.
Draw Call Minimization	Tick-frame event batching	Emitting only salient events (e.g. cluster_formed, translation_detected) reduces simulation “chatter.”
Texture Compression	Salience field sparsity	Sparse ψ(x) fields compress naturally; only high-salience zones need full resolution.
BVH / Octree Acceleration	Spatial indexing of clusters	You could index clusters by salience density or SPBI to accelerate anomaly detection.
Shader Simplification	Rule minimalism (e.g. dimension-neutral propagation)	Simple, universal rules scale better across dimensions — like optimizing shaders for GPU pipelines.
Neural Rendering / GSplat	SPBI-driven narrative overlays	Instead of rendering raw ψ(x), you narrate emergent behavior (e.g. “translation detected”) — like GSplat inferring structure from sparse data.
📡 Minimal Event Schema
text
tick_start:
  { tick }

unit_detected:
  { id, pos, r, S, σ, age }

binding_attempt:
  { id1, id2, d, g }

composite_formed:
  { id_comp, members: [id1, id2], pos, S_total, σc }

composite_decay:
  { id_comp, reason: "instability" }

translation_detected:
  { id, vector, speed }

tick_end:
  { tick, counts: { units, composites } }
🧭 Notes
Use γ ≈ 0.004 for universe-like behavior; apply LOD and instancing aggressively to keep streams light.

Horizon-aware culling guarantees causality in narratives; longer T increases temporal resolution inside the cone, not beyond it.

Index clusters by salience density and σ for fast neighborhood queries and interaction checks.

🖼️ Diagram Reference
See: Tick-frame causal cone

Observer at origin

Horizon boundary moving outward at propagation speed

Visible region inside cone (blue)

Invisible region beyond horizon (red)

Dashed line = horizon

Angle θ = propagation limit