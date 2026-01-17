# Experiment 51c: Results and Interpretation

**Status:** Completed  
**Outcome:** Two‑zone behavior (planet vs. space), no smooth gradient γ(r)

---

## 1. Raw Output Summary

### Simulation setup

- Grid size: 100×100
- Chunk size: 10×10
- Total chunks: 100
- Planet radius: 10
- Planet tick_budget: 5
- Space tick_budget: 1
- Chunk capacity: 50
- Substrate ticks: 20 000

### Radial time dilation results

The simulation measured γ_eff along the +x axis from the center.

| r  | gamma_eff | ticks_processed | ticks_substrate | tick_budget |
|----|-----------|-----------------|-----------------|-------------|
| 1  | 0.052     | 1039            | 20000           | 5           |
| 6  | 0.051     | 1029            | 20000           | 5           |
| 11 | 0.251     | 5025            | 20000           | 1           |
| 16 | 0.248     | 4957            | 20000           | 1           |
| 21 | 0.250     | 4992            | 20000           | 1           |
| 26 | 0.246     | 4930            | 20000           | 1           |
| 31 | 0.249     | 4984            | 20000           | 1           |
| 36 | 0.247     | 4944            | 20000           | 1           |
| 41 | 0.252     | 5032            | 20000           | 1           |
| 46 | 0.249     | 4982            | 20000           | 1           |

### Observed pattern

- **Planet region (r ≤ 6):** γ_eff ≈ 0.05
- **Space region (r ≥ 11):** γ_eff ≈ 0.25
- **No intermediate values**
- **No smooth transition**

This produces a **binary two‑zone system**.

---

## 2. Gradient Analysis

### Monotonicity

- Monotonic increases: `4/9`
- Interpretation: **no clear monotonic trend**

### 1/r² falloff fit

- Best fit k: `≈ 570.27 ± 523.75`
- RMSE: `≈ 180.10`
- Interpretation: **no meaningful 1/r² relationship**

### Visualization

- `time_dilation_results_51c.png` generated
- Shows two flat plateaus (planet vs. space)

---

## 3. Interpretation

Experiment 51c successfully demonstrated:

### ✔ Space as sample‑entities works
Each cell has its own γ_eff, BUSY/IDLE state, and tick history.

### ✔ Planetary region is heavily time‑dilated
γ_eff ≈ 0.05 inside the planet is expected and correct.

### ✔ Space region runs faster
γ_eff ≈ 0.25 outside the planet is also correct.

### ✘ But no smooth gradient emerges
Instead of a gravitational‑like curve, the system forms:

- **one saturated chunk** (planet)
- **many unsaturated chunks** (space)

This is a direct consequence of **chunk‑level locality**:

- Saturation is local *within* a chunk
- But does **not propagate** to neighboring chunks
- Therefore no radial gradient can form

This is the key limitation of 51c.

---

## 4. Ontological Significance

51c proves:

- Local capacity **does** create local time dilation
- But chunking is too coarse to produce geometry
- Space needs **cell‑level** interactions, not chunk‑level
- Gravity cannot emerge without **diffusion of saturation**

This leads directly to Experiment 51d.

---

## 5. Lessons for Next Experiments

### What 51c teaches us

- Locality must be **finer** than chunk size
- Saturation must **flow** between neighboring cells
- Geometry requires **continuous** interactions
- Chunk boundaries destroy gradients

### What 51d introduces

- Cell‑level diffusion of saturation
- Continuous field dynamics
- First attempt at emergent gravitational potential

---

## 6. Role of Experiment 51c in the Research Arc

- **51:** global saturation, no geometry
- **51b:** granular matter, no space
- **51c:** space as sample‑entities, but no diffusion
- **51d:** space + diffusion → field dynamics

51c is the experiment that revealed:

> “Local time dilation exists, but without diffusion there is no geometry.”

It is the bridge between discrete locality (chunks) and continuous locality (cells).
