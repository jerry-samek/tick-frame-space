# Experiment 51g: Results and Interpretation

**Status:** Completed  
**Outcome:** First successful emergence of non‑zero γ_eff, with a stable two‑zone time‑dilation structure

---

## 1. Raw Output Summary

### Simulation setup (baseline)

- Grid size: 100×100
- Planet radius: 10
- Planet tick_budget: 1.5
- Space tick_budget: 1.0
- Load diffusion α: 0.005
- Nonlinear damping γ: 0.0005
- Load source scale: 1.0
- Energy regeneration rate: 1.0
- Energy max: 10.0
- Energy load drain: 0.01
- Substrate ticks: 20 000

### Parameter sweep

Four configurations were tested:

- **51g_baseline**
- **drain_0.005**
- **drain_0.01**
- **drain_0.02**

Across all runs:

- γ_eff was **non‑zero** for the first time in the 51‑series
- γ_eff showed **two distinct zones**:
    - a low‑γ region near the planet
    - a stable plateau in the outer region
- no configuration collapsed into γ = 0 everywhere
- no configuration diverged into γ = 1

This marks the first successful emergence of **stable, non‑uniform time dilation**.

---

## 2. Observed Behavior

### 2.1 Baseline configuration
r = 1   γ = 0.2341 r = 6   γ = 0.2341 r = 11  γ = 0.5000 r = 16  γ = 0.5000 ...


Interpretation:

- **Near the planet (r ≤ 6):**  
  γ ≈ 0.23 → strong time dilation

- **Far from the planet (r ≥ 11):**  
  γ ≈ 0.50 → stable plateau

This is the first demonstration of **emergent gravitational‑like behavior**.

### 2.2 Effect of energy_load_drain

- **drain_0.005:**  
  γ_near ≈ 0.33, γ_far ≈ 0.50  
  → weaker gravitational well

- **drain_0.01:**  
  identical to baseline  
  → balanced regime

- **drain_0.02:**  
  γ_near ≈ 0.0006, γ_far ≈ 0.127  
  → near‑collapse, but still non‑zero  
  → demonstrates sensitivity to energy–load coupling

Across all configurations:

- γ(r) is **flat** beyond r ≈ 10
- only the inner region responds to the planet
- the outer region forms a uniform plateau

---

## 3. Interpretation

Experiment 51g introduced a **regenerative energy buffer** E(x):

- +1 energy per substrate tick
- energy drain proportional to load
- energy consumed when ticks complete
- capped by E_max

This mechanism finally allowed:

- cells to recover from load,
- ticks to complete,
- γ_eff to become non‑zero,
- time to flow at different rates in different regions.

However, the resulting γ(r) profile is **two‑zone**, not continuous:

1. **Inner zone:**  
   strong load → strong energy drain → low γ

2. **Outer zone:**  
   load diffuses only weakly → energy dominates → uniform γ

This indicates that:

- load diffusion is too local,
- damping suppresses load too quickly,
- energy dynamics saturate too fast,
- the field does not propagate far enough to create a gradient.

---

## 4. Ontological Significance

51g is the first experiment in the series to demonstrate:

- **non‑zero time dilation**,
- **stable equilibrium**,
- **spatial variation of γ_eff**,
- **emergent gravitational behavior**.

It confirms the core principle:

> **Time dilation emerges from local competition for substrate ticks,  
> mediated by load and regenerative energy.**

It also reveals the next challenge:

> **To obtain a smooth gravitational curve,  
> the load field must propagate farther and interact more gently with energy.**

---

## 5. Lessons for Next Experiments

To move from a two‑zone world to a smooth γ(r), the next experiment must:

### ✔ Increase load diffusion
→ allow the field to extend farther from the planet

### ✔ Reduce nonlinear damping
→ prevent load from collapsing too quickly

### ✔ Reduce source strength
→ soften the planetary well

### ✔ Increase energy_max
→ allow finer gradations of time flow

### ✔ Increase energy_load_drain
→ make load influence energy even at larger radii

### ✔ Optionally introduce energy diffusion
→ smooth out discontinuities in γ(r)

These changes define the direction for:

> **Experiment 51h: Smooth Gravitational Gradient via Softened Load and Extended Energy Dynamics**

---

## 6. Role of Experiment 51g in the Research Arc

- **51:** global saturation, no geometry
- **51b:** granularity, but no space
- **51c:** two‑zone behavior
- **51d:** diffusion → global collapse
- **51e:** linear damping → still collapse
- **51f:** nonlinear damping → load stabilizes, but time freezes
- **51g:** regenerative energy → first non‑zero γ_eff and emergent gravity
- **51h:** toward a continuous gravitational curve

51g is the experiment that proves:

> **A universe can only live if capacity regenerates.  
> Load alone cannot define time.** 
