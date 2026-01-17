# Experiment 51b: Results and Interpretation

**Status:** Completed  
**Outcome:** Global time‑dilation offset, no spatial gradient

---

## 1. Raw Output Summary

### Simulation setup

- Planet represented as a **cluster of many small entities**
- No explicit space representation (no sample‑entity grid)
- Global scheduler with global capacity
- Planetary entities: `tick_budget = 5`
- Probe entities: `tick_budget = 1`
- Substrate ticks: 20 000
- Probes placed at increasing distances from the planetary cluster

### Observed γ_eff values

All probes — regardless of distance — showed approximately:

- `gamma_eff ≈ 0.16`
- `ticks_processed ≈ 3200`
- `ticks_substrate = 20000`

Planetary entities showed:

- `gamma_eff ≈ 0.03`
- `ticks_processed ≈ 600`
- `ticks_substrate = 20000`

### Pattern summary

- Planetary cluster: **very slow time**
- All probes: **uniformly slowed time**
- No dependence on distance
- No gradient
- No falloff
- No geometric structure

---

## 2. Gradient Analysis

### Monotonicity

- Monotonic increases: `0/N`
- Interpretation: **no monotonic trend**

### 1/r² falloff fit

- Not meaningful — γ_eff is constant across all r
- Any attempt to fit `(1 − γ) ~ 1/r²` yields noise

### Visualization

- γ(r) is a **flat line**
- No curvature
- No slope
- No structure

---

## 3. Interpretation

Experiment 51b demonstrated:

### ✔ Granular matter works
Replacing a single hypertrophic entity with a cluster of many small entities:

- removes binary cutoff behavior,
- produces smoother BUSY/IDLE dynamics,
- avoids the pathological behavior of Experiment 51.

### ✔ Planetary cluster creates global load
The cluster consumes a large fraction of global capacity, causing:

- γ_eff_planet ≈ 0.03
- γ_eff_space ≈ 0.16

### ✘ But no spatial gradient emerges
Because the scheduler is **global**, all entities compete in the same pool.

This means:

- load is distributed uniformly,
- probes at all distances experience the same slowdown,
- no geometric structure can form.

This is the fundamental limitation of 51b.

---

## 4. Ontological Significance

51b proves:

- Time dilation **can** emerge from tick‑budget competition
- But **global scheduling destroys locality**
- Without locality, there is **no geometry**
- Without geometry, there is **no gravitational field**

This is the key insight that motivates 51c.

---

## 5. Lessons for Next Experiments

### What 51b teaches us

- Granularity alone is not enough
- We need **space as a process**, not as an implicit background
- We need **local capacity**, not global
- We need **local interactions**, not global competition
- We need **propagation of saturation**, not uniform distribution

### What 51c introduces

- Sample‑entity grid
- Local capacity per chunk
- First attempt at spatial structure

### What 51d introduces

- Cell‑level diffusion
- First attempt at emergent field dynamics

---

## 6. Role of Experiment 51b in the Research Arc

- **51:** flawed ontology (single hypertrophic entity)
- **51b:** granular matter, but no space
- **51c:** space as sample‑entities, but no diffusion
- **51d:** space + diffusion, but unstable
- **51e:** stabilized field dynamics (next step)

51b is the experiment that revealed:

> “Granularity is necessary, but without space and locality, gravity cannot emerge.”

It is the bridge between entity‑level competition and spatially structured computation.
