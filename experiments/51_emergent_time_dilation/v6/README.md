# Experiment 51f: Reaction–Diffusion Saturation Field with Nonlinear Damping

**Status:** Proposed experiment  
**Goal:** Introduce a *nonlinear sink* into the saturation field dynamics to achieve a stable, smooth,
gravitational‑like time‑dilation profile γ(r) without global collapse or trivial uniformity.

---

## 1. Motivation

Experiments 51d and 51e demonstrated that:

- **local diffusion** of saturation behaves like a field,
- **capacity penalties** correctly slow down local time,
- but **without a nonlinear sink**, the system inevitably collapses into:
    - global saturation (γ = 0 everywhere), or
    - trivial two‑zone behavior (planet vs. space).

This mirrors classical reaction–diffusion systems:

> **Source + diffusion + linear damping → unstable**  
> **Source + diffusion + nonlinear damping → stable patterns**

Experiment 51f introduces the missing ingredient:  
a **nonlinear damping term** that prevents runaway saturation and allows a stable equilibrium field to form.

---

## 2. Ontological Assumptions

Same as in 51c–51e:

- Space is a 2D grid of sample‑entities.
- Each cell has:
    - tick_budget,
    - BUSY/IDLE state,
    - local saturation L(x),
    - effective capacity C_eff(x),
    - emergent γ_eff.
- Time dilation emerges from competition for tick stream.

51f adds:

- **reaction–diffusion dynamics** for L(x),
- **quadratic damping** to stabilize the field.

---

## 3. Mechanical Model

### 3.1 Space and planet

- Grid: N×N (e.g., 100×100)
- Planet: disk of radius R around center
- Planet tick_budget: B_high (e.g., 1.5)
- Space tick_budget: B_low (e.g., 1.0)

### 3.2 Reaction–diffusion equation for saturation

Let L(x, t) be the saturation at cell x at time t.

We define:

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

Interpretation:

- **α ∇² L** spreads load locally (field propagation)
- **S(x)** injects load (mass-energy analogue)
- **−γ L²** removes load faster when L is large (pressure analogue)

This is the first model capable of:

- preventing runaway collapse,
- preventing trivial uniformity,
- forming a stable, smooth field.

### 3.3 Effective capacity

\[
C_\text{eff}(x) = \max\left(C_\text{min}, \frac{C_0}{1 + k L(x)}\right)
\]

Where:

- C_min is higher than in 51e (e.g., 0.2–0.3)
- k is small (e.g., 0.02–0.05)

### 3.4 BUSY/IDLE dynamics

Same as before:

- A cell starts a tick if capacity allows.
- A BUSY cell consumes capacity until its tick completes.
- γ_eff emerges from ticks_processed / substrate_ticks.

---

## 4. Measurement

As in previous experiments:

- Sample γ_eff along a radial line from the center.
- Plot:
    - γ(r) vs r
    - (1 − γ(r)) vs 1/r²
- Inspect:
    - smoothness,
    - monotonicity,
    - stability over time.

---

## 5. Success Criteria

Experiment 51f is successful if:

- γ(r) is **smooth** and **monotonic**,
- γ(r) is **lowest** near the planet,
- γ(r) approaches a **stable plateau** far away,
- no region collapses to γ = 0,
- no binary two‑zone behavior appears,
- the field remains stable over long runs (20k+ ticks).

Optional:

- (1 − γ(r)) shows approximate 1/r or 1/r² behavior.

Failure modes:

- global freeze (γ = 0 everywhere),
- uniform γ (no field),
- chaotic oscillations,
- collapse into a ring or hotspot.

---

## 6. Expected Outcome

With the nonlinear damping term:

- saturation should form a **stable well** around the planet,
- diffusion should spread the load outward,
- damping should prevent runaway growth,
- capacity should remain above the threshold needed for progress,
- γ(r) should form a **smooth gravitational‑like curve**.

This would be the first demonstration of:

> **A stable, emergent gravitational potential in a tick‑frame universe.**

---

## 7. Role of Experiment 51f in the Research Arc

- **51:** global saturation, no geometry
- **51b:** granularity, but no space
- **51c:** space as sample‑entities, chunk‑local saturation
- **51d:** space + diffusion → unstable collapse
- **51e:** space + linear damping → still unstable
- **51f:** space + nonlinear damping → *first stable field*

51f is the experiment that finally introduces the missing physical ingredient:

> **A nonlinear reaction term that stabilizes the field and allows geometry to emerge.**
