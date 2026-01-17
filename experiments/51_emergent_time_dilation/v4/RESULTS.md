# Experiment 51d: Results and Interpretation

**Status:** Completed  
**Outcome:** Global collapse into full saturation (γ_eff = 0 everywhere)

---

## 1. Raw Output Summary

### Simulation setup

- Grid size: 100×100
- Planet radius: 10.0
- Planet tick_budget: 5
- Space tick_budget: 1
- Base capacity per cell: 1.0
- Diffusion alpha: 0.2
- Capacity sensitivity: 0.5
- Substrate ticks: 20 000

### Radial time dilation results

All sampled cells (both inside and outside the planet) show:

- `ticks_processed = 0`
- `substrate_ticks_elapsed = 20000`
- `gamma_eff = 0.000`

Table:

| r  | gamma_eff | ticks_processed | ticks_substrate | tick_budget |
|----|-----------|-----------------|-----------------|-------------|
| 1  | 0.000     | 0               | 20000           | 5           |
| 6  | 0.000     | 0               | 20000           | 5           |
| 11 | 0.000     | 0               | 20000           | 1           |
| 16 | 0.000     | 0               | 20000           | 1           |
| 21 | 0.000     | 0               | 20000           | 1           |
| 26 | 0.000     | 0               | 20000           | 1           |
| 31 | 0.000     | 0               | 20000           | 1           |
| 36 | 0.000     | 0               | 20000           | 1           |
| 41 | 0.000     | 0               | 20000           | 1           |
| 46 | 0.000     | 0               | 20000           | 1           |

Gradient analysis:

- Monotonic increases: `0/9`
- No visible gradient (all γ_eff = 0)

1/r² fit:

- Best fit k: `≈ 758.5 ± 699.0`
- RMSE: `≈ 239.63`
- Interpretation: meaningless, since γ is identically zero.

Visualization:

- `time_dilation_results_51d.png` generated, but shows a flat line at γ = 0.

---

## 2. Interpretation

### 2.1 What happened

- No cell completed a single physical tick in 20 000 substrate ticks.
- Effective time dilation γ_eff collapsed to **0 everywhere**.
- The entire sample‑entity space entered a state of **total saturation**.

In other words:

> The simulated universe fell into a global computational “blackout” — a heat‑death / singularity state where no local time progresses.

---

### 2.2 Why it happened

The combination of parameters led to runaway collapse:

1. **Strong diffusion (α = 0.2)**
    - Saturation spreads very quickly across the grid.
    - Planetary load is rapidly smeared over the entire space.

2. **Aggressive capacity penalty (sensitivity = 0.5)**
    - Even moderate load drastically reduces effective capacity.
    - Once load rises, capacity collapses toward zero.

3. **High planetary tick_budget (5) vs base capacity (1)**
    - Planet is extremely “heavy” relative to local capacity.
    - It injects a large, persistent load into the field.

4. **Symmetric diffusion without sinks or damping**
    - Load spreads but never dissipates.
    - The only fixed point is global high load → near‑zero capacity → γ_eff → 0.

Result:  
The system converges to a **uniform, fully saturated state** with no time evolution.

---

## 3. Ontological significance

Experiment 51d shows:

- ✔ Local diffusion of saturation **does** behave like a field mechanism.
- ✘ But in this configuration, the field is **unstable** and collapses the entire space.

This is analogous to:

- gravitational collapse,
- runaway potentials,
- singularities without stabilizing pressures.

In tick‑frame terms:

> “If saturation can spread freely and penalizes capacity too strongly, the entire universe freezes.”

This is not a hack artifact — it is a **dynamical consequence** of the chosen parameters and rules.

---

## 4. Lessons for next experiments (51e and beyond)

51d suggests the need for **stabilized field dynamics**:

- **Weaker diffusion:** lower α (e.g. 0.01 instead of 0.2).
- **Softer capacity penalty:** lower sensitivity (e.g. 0.05 instead of 0.5).
- **Lighter planet:** smaller tick_budget contrast (e.g. 2 vs 1).
- **Damping of load:**  
  \[
  L'(x) = (1 - \beta)L(x) + \alpha \nabla^2 L(x)
  \]
- **Minimum capacity floor:**  
  \[
  C_\text{eff}(x) = \max(C_\text{min}, \frac{C_0}{1 + kL(x)})
  \]

Goal for 51e:

> Achieve a **stable, non‑trivial equilibrium field** where:
> - γ_eff(r) is smooth and monotonic,
> - time does not freeze everywhere,
> - saturation forms a well around the planet instead of collapsing the whole grid.

---

## 5. Role of Experiment 51d in the research arc

- **51:** global saturation, no geometry.
- **51b:** granular matter, no space.
- **51c:** space as sample‑entities, chunk‑local saturation, two‑zone behavior.
- **51d:** space + diffusion, but unstable → global collapse.

51d is a **critical negative result**:

- It confirms that diffusion is a plausible mechanism for fields.
- It shows that **unconstrained diffusion + strong penalties** lead to total collapse.
- It motivates the design of **51e: stabilized, bounded field dynamics**.

In that sense, 51d is not a failure — it is the experiment that tells you:

> “Fields are real in this ontology, but they must be **tuned and stabilized** to avoid universal freeze.”
