# Experiment 51e: Results and Interpretation

**Status:** Completed  
**Outcome:** Repeated global freeze (γ_eff = 0 everywhere) across all tested configurations

---

## 1. Raw Output Summary

### Simulation setup (baseline)

- Grid size: 100×100
- Planet radius: 10.0
- Planet tick_budget: 2
- Space tick_budget: 1
- Base capacity: 1.0
- Capacity sensitivity: 0.05
- Capacity minimum: 0.05
- Diffusion alpha: 0.01
- Diffusion beta: 0.005
- Substrate ticks: 20 000

### Parameter sweep (example)

Tested configurations:

- `alpha_0.005`
- `alpha_0.01`
- `alpha_0.02`

In all cases:

- `gamma_eff(r) = 0.0000` for all sampled radii
- no cell completed a single physical tick
- the entire grid ended in full saturation

---

## 2. Observed Behavior

Across all runs:

- γ_eff = 0 near the planet
- γ_eff = 0 in the surrounding space
- γ_eff = 0 even far from the planet

This means:

> **No cell ever completed a tick.  
> Effective capacity remained permanently below the threshold required to make progress.**

The system converges to:

- full load saturation,
- effective capacity → capacity_min,
- no physical time progression.

---

## 3. Interpretation

Experiment 51e aimed to:

- stabilize saturation diffusion,
- prevent the global collapse seen in 51d,
- allow a smooth γ(r) profile to emerge.

The results show that:

1. **The load model is purely source‑driven**
    - every cell generates load ∝ tick_budget every tick,
    - load never “discharges,” it only spreads.

2. **Damping is too weak and purely linear**
    - the linear factor (1 − β) cannot counteract a constant source,
    - load grows until capacity collapses to its minimum.

3. **Capacity_min is too low**
    - once C_eff < 1.0, a cell cannot complete tick_budget = 1,
    - γ_eff remains 0 indefinitely.

Consequence:

> **Without a true nonlinear sink mechanism, global freeze is the inevitable attractor of the system.**

---

## 4. Ontological Significance

51e confirms:

- saturation diffusion behaves like a field,
- the field affects capacity,
- capacity affects time,
- time can globally collapse.

It also shows:

- “source + diffusion + linear damping” is insufficient,
- the system requires a **nonlinear sink**,
- otherwise the only stable state is total saturation.

This mirrors:

- gravitational collapse without pressure,
- potentials without stabilizing terms,
- reaction–diffusion systems without nonlinear damping.

---

## 5. Lessons for Next Experiments

51e makes it clear that the next step must:

- introduce **nonlinear damping** (e.g., −γ·L²),
- cap maximum saturation (L_max),
- ensure capacity never drops below a value that prevents all progress,
- define equilibrium as **statistical balance**, not “low load.”

This naturally leads to:

> **Experiment 51f: Reaction–diffusion saturation with nonlinear damping**  
> (source + diffusion + nonlinear sink → stable field)

---

## 6. Role of Experiment 51e in the Research Arc

- **51:** global saturation, no geometry
- **51b:** granularity, but no space
- **51c:** space as sample‑entities, chunk‑local saturation, two‑zone world
- **51d:** space + diffusion, unstable → global collapse
- **51e:** space + stabilization 1.0, but still global freeze
- **51f:** space + reaction–diffusion field with nonlinear damping (next step)

51e is the experiment that says:

> “The field mechanism is correct,  
> but without a nonlinear sink,  
> a stable universe in this model is impossible.”
