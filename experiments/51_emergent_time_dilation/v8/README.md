# Experiment 51h: Smooth Gravitational Gradient via Softened Load and Extended Energy Dynamics

**Status:** Proposed experiment  
**Goal:** Transform the two‑zone time‑dilation profile of 51g into a continuous, smooth γ(r) curve by softening the load
field, extending its spatial reach, and refining the coupling between load and energy.

---

## 1. Motivation

Experiment 51g achieved a major breakthrough:

- γ_eff became non‑zero for the first time,
- time dilation emerged near the planet,
- the system reached a stable equilibrium.

However, the resulting γ(r) profile was **two‑zone**:

- strong dilation near the planet,
- flat plateau in the outer region.

This indicates that:

- the load field L(x) is too localized,
- nonlinear damping suppresses it too quickly,
- energy dynamics saturate too fast,
- the field does not propagate far enough to create a gradient.

Experiment 51h aims to fix this by softening the field and extending its influence.

---

## 2. Ontological Assumptions

Same as in 51g:

- Space is a grid of sample‑entities.
- Each cell has:
    - tick_budget,
    - load L(x),
    - energy E(x),
    - BUSY/IDLE state,
    - emergent γ_eff.

51h modifies:

- load diffusion,
- damping strength,
- energy capacity,
- energy–load coupling,
- optional energy diffusion.

The goal is to create a **continuous gravitational potential**.

---

## 3. Mechanical Model

### 3.1 Load field (softened)

We retain the reaction–diffusion form:

\[
L_{t+1}(x) = L_t(x)

+ \alpha \nabla^2 L_t(x)
+ S(x)

- \gamma L_t(x)^2
  \]

But with key changes:

- **higher diffusion α** → field spreads farther
- **lower damping γ** → field decays more slowly
- **lower source S(x)** → planet is less extreme

This allows L(x) to form a **long‑range gradient**.

---

## 4. Energy dynamics (extended)

Energy evolves as:

\[
E_{t+1}(x) =
\min\left(E_\text{max},\;
E_t(x) + R - \text{work\_cost}(x) - D \cdot L_t(x)\right)
\]

51h modifies:

- **higher E_max** → more resolution in γ
- **higher load drain D** → load influences energy farther out
- **optional energy diffusion**:

\[
E_{t+1}(x) += \beta \nabla^2 E_t(x)
\]

This smooths discontinuities in γ(r).

---

## 5. Expected Behavior

If parameters are chosen correctly:

- load spreads outward in a soft gradient,
- energy is drained proportionally to load,
- energy regenerates everywhere but at different rates,
- γ_eff becomes a **smooth, monotonic function of r**.

We expect:

- γ_near ≪ γ_far
- γ_far < 1
- no plateaus
- no sharp transitions
- no collapse
- no runaway

This would be the first true **gravitational potential** in the tick‑frame universe.

---

## 6. Success Criteria

51h is successful if:

- γ(r) is smooth and monotonic,
- γ(r) has no flat plateau,
- γ(r) has no discontinuities,
- γ(r) stabilizes over long runs (20k+ ticks),
- γ(r) resembles a potential well.

Optional:

- (1 − γ(r)) approximates 1/r or 1/r².

---

## 7. Suggested Parameter Ranges

These ranges are designed to soften the field:

- diffusion_alpha: **0.01 – 0.02**
- damping_gamma: **0.00005 – 0.0002**
- source_scale: **0.3 – 0.6**
- energy_max: **20 – 50**
- energy_load_drain: **0.02 – 0.05**
- energy_diffusion_beta: **0.001 – 0.01** (optional)

These values encourage:

- long‑range load propagation,
- gentle decay,
- smooth energy distribution,
- continuous γ(r).

---

## 8. Role of Experiment 51h in the Research Arc

- **51:** global saturation
- **51b:** granularity
- **51c:** two‑zone world
- **51d:** collapse
- **51e:** collapse
- **51f:** stable load, frozen time
- **51g:** stable time, two‑zone dilation
- **51h:** smooth gravitational gradient

51h is the experiment that aims to produce:

> **the first continuous, emergent gravitational potential  
> in the tick‑frame universe.**
