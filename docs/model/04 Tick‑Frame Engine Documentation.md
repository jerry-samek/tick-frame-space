# Tick‑Frame Engine Documentation

---

## Section 1: Rendering Pipeline

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


## Section 2: Horizon Buffer and Wave Length in Tick‑Frame Engines

### Abstract
This paper formalizes temporal invariance in tick‑frame substrates. Unlike classical spatial metrics, the tick‑frame engine defines “length” as a constant temporal horizon. The system maintains this horizon by continuously shifting the buffer: discarding the oldest tick and appending a new tick at the leading edge. This mechanism ensures reproducibility, causality, and invariance of observable dynamics.

### 1. Introduction
Tick‑frame substrates evolve through discrete updates, prioritizing causality and reproducibility over absolute metrics. The concept of “length” is reframed as the number of ticks inside a constant horizon window, a wave‑like envelope that advances through time without altering its form.

### 2. Tick‑Frame Universe Model Background
- **State space:**  
  \[
  \psi: \mathbb{Z}^d \times \mathbb{Z}_{\ge 0} \to \mathbb{R}^m
  \]  
- **Update operator:**  
  \[
  \psi_{t+1} = F(\psi_t; \gamma, \alpha_0, \theta)
  \]  
- **Parameters:** γ (propagation speed), α₀ (initial amplitude), θ (rule configuration), seed (deterministic initialization).  
- **Observers:** Perceive only the horizon slice \(\mathcal{H}(t)\).

### 3. Horizon Buffer Formalization
\[
\mathcal{H}(t) = \{ \psi(x, t-k) \mid k = 0, 1, \dots, H-1 \}
\]

- Constant buffer size H.  
- Sliding window: drop oldest tick, append newest.  
- Causal cone enforced by γ.  
- Persistence and drift defined relative to horizon.

### 4. Measurement Without Absolute Length
- **Temporal meter:**  
  \[
  L_{\text{temporal}} := H \text{ ticks}
  \]  
- **Effective wavelength:**  
  \[
  \lambda_{\text{eff}}(u) = \frac{H}{n_{\text{cycles}}(u)}
  \]  
- Drift normalized by γ and H.  
- No fixed meters; scale inferred from rhythms.

### 5. Sliding Horizon Diagram

Time axis →
 …  t-H+3      t-H+2      t-H+1        t        t+1
     [ψ]         [ψ]         [ψ]        [ψ]      [ψ]
       \           \           \         |        |
        \           \           \        | append new tick
         \           \           \       v
  H-buffer window: [ ψ(t-H+1) | ψ(t-H+2) | … | ψ(t-1) | ψ(t) ]
                     ^                         ^
                     |                         |
          drop oldest tick             current leading edge

---

## Section 3: Appendix A — Cosmological Expansion vs. Tick‑Frame Universe Model

### A.1 Scientific Observations
- Accelerating expansion attributed to dark energy.  
- Hubble tension between early and late universe measurements.  
- DESI hints at evolving dark energy → possible slowing.  
- Observable universe bounded by cosmic horizon (speed of light).

### A.2 Comparative Framework

| **Concept**                  | **Expanding Universe (Cosmology)**                                                                 | **Tick‑Frame Universe Model**                                                                 |
|-------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Expansion driver**          | Dark energy / cosmological constant                                                              | Horizon buffer invariance; expansion emerges from sliding tick window                         |
| **Scale definition**          | Distances via redshift (meters, parsecs, light‑years)                                            | “Length” = number of ticks in horizon buffer; temporal not spatial                            |
| **Causal horizon**            | Observable universe limited by speed of light                                                    | Causal cone enforced by γ; superluminal events culled                                         |
| **Expansion rate**            | Hubble constant (H₀) measures recession velocity per unit distance                               | Effective scaling rate defined by γ and buffer size H                                         |
| **Acceleration vs. slowing**  | Debate: accelerating vs. slowing expansion                                                       | Changing H mimics acceleration/deceleration                                                   |
| **Measurement protocol**      | Redshift surveys, CMB, supernovae                                                                | Tick counts, cycles, drift variance; deterministic logs                                       |
| **Falsifiability**            | Competing models tested against data (ΛCDM vs. evolving dark energy)                             | Parameters (γ, H, θ) versioned; replay with seeds ensures falsifiability                      |

### A.3 Conceptual Bridge
- Cosmology: expansion observed as galaxies receding faster over time.  
- Tick‑frame: expansion encoded in sliding buffer; observables scale with time.  
- Shared challenge: both replace fixed rulers with dynamic horizons.

### A.4 Implications
- Tick‑frame model provides computational analogue to cosmological expansion.  
- Tuning H and γ simulates accelerating, constant, or slowing expansion.  
- Framework is falsifiable and auditable, offering a bridge between computation and cosmology.