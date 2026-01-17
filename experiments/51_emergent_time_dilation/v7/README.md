# Experiment 51g: Reaction–Diffusion Load Field with Regenerative Energy Dynamics

**Status:** Proposed experiment  
**Goal:** Introduce a regenerative per‑cell energy buffer that restores computational capacity each causal tick, enabling stable, non‑zero γ_eff and allowing a smooth gravitational‑like time‑dilation field to emerge.

---

## 1. Motivation

Experiments 51d–51f revealed a fundamental limitation:

- load L(x) was dynamic (diffusion, damping, source),
- but capacity C_eff(x) was **not** dynamic,
- it was only an algebraic penalty based on L(x),
- once suppressed, capacity could never recover.

This made global freeze (γ = 0 everywhere) the only stable attractor.

However, in the **original tick‑frame theory**, every entity receives:

> **one unit of energy per causal tick**,  
> which is then spent when the entity performs work.

This regenerative mechanism is essential for:

- preventing permanent freeze,
- allowing progress even under load,
- producing stable equilibrium rather than collapse.

Experiment 51g introduces this missing mechanism.

---

## 2. Ontological Assumptions

Same as in 51c–51f:

- Space is a 2D grid of sample‑entities.
- Each cell has:
    - tick_budget,
    - BUSY/IDLE state,
    - local saturation L(x),
    - local energy E(x),
    - emergent γ_eff.

51g adds:

- **regenerative energy dynamics**,
- **coupling between load and energy**,
- **two‑equation system** for L(x) and E(x).

---

## 3. Mechanical Model

### 3.1 Space and planet

- Grid: N×N (e.g., 100×100)
- Planet: disk of radius R around center
- Planet tick_budget: B_high (e.g., 1.5)
- Space tick_budget: B_low (e.g., 1.0)

### 3.2 Reaction–diffusion load field

Same stabilized form as 51f:

\[
L_{t+1}(x) = L_t(x)
+ \alpha \nabla^2 L_t(x)
+ S(x)
- \gamma L_t(x)^2
  \]

Where:

- **α** = diffusion coefficient
- **S(x)** = source term (planetary load)
- **γ** = nonlinear damping coefficient

This produces a stable load field.

### 3.3 Regenerative energy buffer

Each cell has energy E(x):

\[
E_{t+1}(x) =
\min\left(E_\text{max},\;
E_t(x) + R - \text{work\_cost}(x) - D \cdot L_t(x)\right)
\]

Where:

- **R** = regeneration rate (typically 1 per tick)
- **work_cost(x)** = tick_budget if a tick completes
- **D** = load‑induced energy drain
- **E_max** = maximum energy buffer

Interpretation:

- energy regenerates every tick,
- load slows regeneration (but cannot stop it),
- work consumes energy,
- energy cannot exceed E_max.

### 3.4 Work execution

A cell can start or continue work only if:

\[
E_t(x) \ge \text{tick\_budget}
\]

This ensures:

- heavy regions (near planet) accumulate energy slowly → slower time,
- light regions accumulate energy quickly → faster time.

### 3.5 Emergent time dilation

As before:

\[
\gamma_\text{eff}(x) =
\frac{\text{ticks\_processed}(x)}{\text{substrate\_ticks}}
\]

---

## 4. Measurement

Same methodology as previous experiments:

- sample γ_eff along a radial line from the center,
- plot γ(r) vs r,
- plot (1 − γ(r)) vs 1/r²,
- inspect:
    - smoothness,
    - monotonicity,
    - stability over time.

---

## 5. Success Criteria

Experiment 51g is successful if:

- γ(r) is **smooth** and **monotonic**,
- γ(r) is **lowest** near the planet,
- γ(r) approaches a **stable plateau** far away,
- no region collapses to γ = 0,
- no binary two‑zone behavior appears,
- the field remains stable over long runs (20k+ ticks).

Optional:

- (1 − γ(r)) shows approximate 1/r or 1/r² behavior.

Failure modes:

- energy runaway (E → E_max everywhere),
- energy starvation (E → 0 everywhere),
- chaotic oscillations,
- collapse into rings or hotspots.

---

## 6. Expected Outcome

With regenerative energy:

- cells can always eventually complete ticks,
- γ_eff becomes non‑zero everywhere,
- load still slows time near the planet,
- energy dynamics prevent permanent freeze,
- the system can reach a **stable equilibrium**.

This should produce:

> **the first stable, gravitational‑like γ(r) curve in the tick‑frame universe.**

---

## 7. Role of Experiment 51g in the Research Arc

- **51:** global saturation, no geometry
- **51b:** granularity, but no space
- **51c:** space as sample‑entities, two‑zone behavior
- **51d:** diffusion → global collapse
- **51e:** linear damping → still collapse
- **51f:** nonlinear damping → load stabilizes, but time freezes
- **51g:** regenerative energy → first chance at stable γ(r)

51g is the experiment that finally introduces:

> **the regenerative mechanism required for a living, evolving universe.**
