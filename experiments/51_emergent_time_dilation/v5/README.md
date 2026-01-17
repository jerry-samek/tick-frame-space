# Experiment 51e: Stabilized Saturation Field and Emergent Time Dilation

**Status:** Proposed experiment  
**Goal:** Test whether a *stabilized, locally diffusing saturation field* can produce a smooth, non‑trivial time‑dilation profile γ(r) around a planetary mass distribution, without collapsing the entire space into full saturation (γ = 0) or splitting it into binary zones.

---

## 1. Motivation

Experiment 51d introduced **local diffusion of saturation** between neighboring sample‑entities and showed that:

- saturation behaves like a field,
- but with the chosen parameters, the field is **unstable**,
- the entire grid collapsed into **global saturation**,
- no cell completed a single physical tick (γ_eff = 0 everywhere).

This is analogous to a universe collapsing into a singularity:  
the mechanism is correct in spirit, but **unbounded**.

Experiment 51e introduces **stabilized field dynamics**:

- weaker diffusion,
- softer capacity penalties,
- damping of saturation,
- a minimum capacity floor,
- a lighter planet.

The goal is to obtain a **stable, structured field**:

- γ(r) smooth and monotonic,
- γ(r) < 1 near the planet,
- γ(r) → constant far away,
- no global freeze.

---

## 2. Ontological Assumptions

Same core ontology as 51c/51d:

- space = grid of sample‑entities,
- each cell has tick_budget, local state, γ_eff,
- time dilation is a local property of space,
- gravity emerges from competition for tick stream.

51e adds:

- **stabilized diffusion** of saturation,
- **bounded response** of capacity to load.

---

## 3. Mechanical Model

### 3.1 Space and planet

- 2D grid of sample‑entities, e.g. 100×100.
- Planet = disk of radius R around the center.
- Inside planet: `tick_budget = B_high` (e.g. 2).
- Outside planet: `tick_budget = B_low` (e.g. 1).

### 3.2 Load and diffusion

Each substrate tick:

1. Compute raw load field \(L(x)\) from local demand:
    - demand ∝ tick_budget (and/or BUSY state),
    - normalized by base capacity.

2. Apply **damped diffusion**:
   \[
   L'(x) = (1 - \beta)L(x) + \alpha \nabla^2 L(x)
   \]
   where:
    - \(\alpha\) is the diffusion coefficient (small, e.g. 0.01),
    - \(\beta\) is a damping factor (e.g. 0.001–0.01),
    - \(\nabla^2\) is the discrete Laplacian over neighbors.

This ensures:

- load spreads locally,
- but also decays over time,
- preventing runaway growth.

### 3.3 Effective capacity

Effective capacity per cell:

\[
C_\text{eff}(x) = \max\left(C_\text{min}, \frac{C_0}{1 + k L(x)}\right)
\]

- \(C_0\): base capacity (e.g. 1.0),
- \(k\): sensitivity (small, e.g. 0.05),
- \(C_\text{min}\): minimum capacity floor (e.g. 0.05).

This ensures:

- high load reduces capacity,
- but capacity never reaches zero,
- preventing total freeze.

### 3.4 BUSY/IDLE dynamics

Same as before:

- BUSY cells consume work if capacity allows,
- IDLE cells start new ticks if capacity is sufficient,
- γ_eff emerges from ticks_processed / substrate_ticks.

---

## 4. Measurement

As in 51c/51d:

- choose cells along a radial line: \((x_0 + r, y_0)\),
- measure γ_eff(r) after N substrate ticks,
- plot:
    - γ(r) vs r,
    - (1 − γ(r)) vs 1/r².

---

## 5. Success Criteria

The experiment is considered successful if:

- γ(r) is **smooth** (no sharp jumps),
- γ(r) is **monotonic increasing** with r (or nearly so),
- γ(r) is **significantly lower** near the planet than far away,
- γ(r) approaches a **stable plateau** at large r,
- no region has γ_eff ≈ 0 everywhere,
- no binary two‑zone behavior (planet vs space only).

Optional:

- (1 − γ(r)) vs 1/r² shows a coherent trend (not necessarily perfect).

The experiment fails if:

- γ_eff collapses to 0 everywhere (global freeze),
- γ_eff is constant everywhere (no field),
- γ(r) shows only two plateaus (planet vs space),
- results are extremely sensitive to small parameter changes.

---

## 6. Expected Outcome

If the stabilized dynamics are well‑tuned:

- the planet will create a **saturation well**,
- saturation will diffuse outward but remain bounded,
- γ(r) will be lowest at r ≈ 0 and rise smoothly with r,
- far from the planet, γ(r) will approach a constant < 1,
- the field will resemble a **soft gravitational potential**.

This would be the first demonstration of a:

> **stable, emergent time‑dilation field in a tick‑frame universe.**

---

## 7. Role of Experiment 51e in the Research Arc

- **51:** global saturation, no geometry.
- **51b:** granular matter, no space.
- **51c:** space as sample‑entities, chunk‑local saturation, two‑zone behavior.
- **51d:** space + diffusion, unstable → global collapse.
- **51e:** space + stabilized diffusion → *candidate gravitational field*.

51e is the first experiment explicitly designed to:

- keep the ontology clean,
- keep the dynamics local,
- but **stabilize** the field so that geometry can emerge without destroying the universe.
