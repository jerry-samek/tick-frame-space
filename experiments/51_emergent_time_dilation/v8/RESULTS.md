# Experiment 51h: Results and Interpretation

**Status:** Completed  
**Outcome:** Smooth but extremely shallow γ(r); gravitational field too weak to produce meaningful curvature

---

## 1. Raw Output Summary

### Simulation setup (baseline)

- Grid size: 100×100
- Planet radius: 10
- Planet tick_budget: 1.5
- Space tick_budget: 1.0
- Load diffusion α: 0.015
- Nonlinear damping γ: 0.0001
- Load source scale: 0.5
- Energy regeneration rate: 1.0
- Energy max: 30.0
- Energy load drain: 0.03
- Energy diffusion β: 0.005
- Substrate ticks: 20 000

### Parameter sweep

Four configurations were tested:

- **51h_baseline**
- **soft_field_1**
- **soft_field_2**
- **with_energy_diffusion**

Across all runs:

- γ_eff was non‑zero everywhere
- γ_eff increased with radius
- γ(r) was smooth and monotonic
- but the magnitude of γ was extremely small (0.001–0.006)
- gravitational well was shallow
- no collapse, no runaway, no plateaus

This confirms that 51h successfully removed the two‑zone structure of 51g, but at the cost of making the field too weak.

---

## 2. Observed Behavior

### 2.1 Baseline configuration

r = 1 γ = 0.0018 r = 6 γ = 0.0018 r = 11 γ = 0.0034 r = 16 γ = 0.0037 r = 21 γ = 0.0037 ...

Interpretation:

- γ(r) is **smooth**, **monotonic**, and **continuous**
- but the difference between near and far is tiny
- gravitational well is extremely shallow
- energy dominates everywhere

### 2.2 soft_field_1

γ_near ≈ 0.0027 γ_far ≈ 0.0065

- slightly stronger gradient
- still extremely weak
- load field too diluted

### 2.2 soft_field_2

γ_near ≈ 0.0013 γ_far ≈ 0.0027

- even weaker than baseline
- load diffusion too strong
- damping too low
- energy too dominant

### 2.3 with_energy_diffusion

- similar behavior
- energy diffusion smooths γ(r)
- but also destroys contrast
- gravitational well becomes even shallower

---

## 3. Interpretation

Experiment 51h achieved its primary goal:

> **γ(r) is no longer two‑zone; it is smooth and continuous.**

However, the gravitational field is **far too weak**:

- load diffuses too quickly
- damping suppresses load accumulation
- source is too soft
- energy_max is too high
- energy diffusion erases gradients
- energy regeneration overwhelms load drain

As a result:

> **The load field cannot create a meaningful energy imbalance,  
> so time dilation remains extremely small.**

This is the opposite failure mode of 51g:

- 51g: field too strong → two‑zone world
- 51h: field too weak → almost flat world

The correct regime lies between them.

---

## 4. Ontological Significance

51h demonstrates that:

- smooth gravitational behavior is possible,
- but requires a delicate balance between load and energy,
- and the field must be neither too hard nor too soft.

This confirms the deeper principle:

> **Gravitation in the tick‑frame universe is a balance between  
> local load propagation and regenerative energy capacity.**

51h shows that:

- long‑range load propagation is necessary,
- but must not be so strong that it erases structure,
- and energy must be limited enough to allow gradients to form.

---

## 5. Lessons for Next Experiments

To obtain a realistic gravitational curve, the next experiment must:

### ✔ Strengthen the load field

- lower diffusion α
- increase source_scale
- increase damping slightly

### ✔ Weaken the energy field

- reduce energy_max
- reduce energy diffusion
- keep energy_load_drain strong

### ✔ Maintain smoothness

- keep damping small enough to avoid collapse
- keep diffusion non‑zero but moderate

These adjustments define the direction for:

> **Experiment 51i: Balanced Load–Energy Regime for Realistic γ(r)**

---

## 6. Role of Experiment 51h in the Research Arc

- **51g:** first non‑zero γ_eff, but two‑zone
- **51h:** first smooth γ(r), but too shallow
- **51i:** target regime between 51g and 51h

51h is the experiment that proves:

> **Smooth gravitational curvature is possible,  
> but requires precise tuning of load and energy dynamics.**
