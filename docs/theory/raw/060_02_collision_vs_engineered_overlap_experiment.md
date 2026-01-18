# TF‑E‑060_02: Collision vs Engineered Overlap
**A concrete experiment to compare brute‑force collisions with engineered pattern composites in a tick‑frame‑like system**

**Category:** Tick‑Frame Experimental Design  
**Status:** Draft  
**Author:** Tom  
**Scope:** Defines a minimal, implementable experiment that contrasts brute‑force collision behavior with engineered pattern overlap in a discrete tick‑based model. Designed as a conceptual analogue to high‑energy collision experiments.

---

## 1. Goal of the experiment

Demonstrate, in a controlled discrete system, that:

1. **Brute‑force collisions** of patterns:
    - rarely produce stable composite objects,
    - mostly lead to destruction, scattering, or short‑lived noise.

2. **Engineered overlaps** of compatible patterns:
    - reliably produce stable composite states,
    - can exhibit heavy‑state‑like behavior (slower local dynamics, higher “maintenance cost”).

This experiment is the tick‑frame analogue of comparing:

- LHC‑style collisions vs.
- deliberately designed bound states.

---

## 2. Model setup

Use a **2D or 3D discrete grid** with synchronous ticks:

- **Cells:** each cell has a finite state (e.g., 0 = empty, 1..N = pattern states).
- **Tick:** at each step, all cells update according to local rules.
- **Patterns:** localized, self‑maintaining configurations that:
    - persist over time,
    - move or oscillate,
    - require non‑zero update work.

### 2.1 Local rules

Define rules such that:

- isolated patterns are **stable** (they maintain their shape),
- patterns can **move** (e.g., gliders, solitons, traveling waves),
- overlapping patterns can:
    - either annihilate,
    - scatter,
    - or form a new composite pattern (if designed to be compatible).

You can start from:

- a custom CA,
- or a modified Life‑like rule,
- or a bespoke tick‑frame engine with explicit “maintenance cost” per region.

---

## 3. Phase A: Brute‑force collision experiment

### 3.1 Setup

1. Define two distinct stable patterns: **P₁** and **P₂**.
2. Place them on a collision course:
    - opposite sides of the grid,
    - moving toward each other,
    - with tunable relative velocity and phase.
3. Run many trials with:
    - different impact parameters (offsets),
    - different velocities,
    - different internal phases (if applicable).

### 3.2 Measurements

For each collision, record:

- **Outcome type:**
    - annihilation,
    - scattering (patterns survive but are deflected),
    - noise (fragmentation into unstable debris),
    - transient composite (short‑lived),
    - stable composite (long‑lived new pattern).

- **Lifetime of any composite state** (in ticks).
- **Local update cost** in the collision region:
    - e.g., number of non‑trivial updates per tick in a bounding box.

### 3.3 Expected result

- Stable composites are **rare** and highly sensitive to initial conditions.
- Most collisions:
    - destroy structure,
    - or produce short‑lived noise.
- This mimics **brute‑force physics**:
    - high energy, low structural control,
    - statistical emergence of interesting states.

---

## 4. Phase B: Engineered overlap experiment

### 4.1 Setup

1. Start from the same base patterns **P₁** and **P₂**.
2. Instead of colliding them at high relative speed, **design an overlap configuration**:
    - place P₁ and P₂ in a partially overlapping arrangement,
    - adjust their relative phase/orientation so that:
        - some internal structure is shared,
        - conflicts are minimized.

3. Optionally define a **third pattern P₃** as the intended composite:
    - P₃ is a known stable pattern,
    - P₁ + P₂ overlap is designed to relax into P₃.

### 4.2 Procedure

- Initialize the grid with the engineered overlap of P₁ and P₂.
- Let the system evolve without external forcing.
- Observe whether:
    - the overlap region stabilizes into a new pattern,
    - the composite has:
        - higher maintenance cost,
        - slower local dynamics,
        - distinct behavior from P₁ and P₂.

### 4.3 Measurements

For the engineered composite:

- **Stability:**
    - lifetime (ticks),
    - robustness to small perturbations.

- **Local update cost:**
    - average number of non‑trivial updates per tick in the composite region.

- **Effective “mass” / heaviness:**
    - e.g., slower propagation,
    - stronger influence on nearby patterns,
    - tendency to attract/deflect other patterns.

### 4.4 Expected result

- Engineered overlap **reliably** produces a stable composite pattern.
- The composite:
    - has higher local update cost,
    - may move more slowly or be more “inertial”,
    - behaves like a **heavy state** in the tick‑frame sense.

This demonstrates that **structural design** outperforms brute‑force collisions for creating stable, extended objects.

---

## 5. Phase C: Direct comparison

Summarize results across many runs:

### 5.1 Metrics

- **Success rate of stable composite formation:**
    - brute‑force collisions vs engineered overlaps.

- **Average lifetime of composites.**
- **Average local update cost (γ‑like measure).**
- **Sensitivity to initial conditions.**

### 5.2 Interpretation

- Brute‑force collisions:
    - low success rate,
    - short lifetimes,
    - high chaos, low predictability.

- Engineered overlaps:
    - high success rate,
    - long lifetimes,
    - predictable behavior,
    - clear heavy‑state signatures.

This mirrors the difference between:

- LHC‑style energy collisions,
- and tick‑frame‑style structural engineering.

---

## 6. Extensions

Once the basic experiment works, you can extend it by:

- adding **multi‑pattern composites** (P₁ + P₂ + P₃),
- exploring **overlap collapse** (deliberately destabilizing the composite),
- measuring **geodesic‑like behavior**:
    - how other patterns move in the vicinity of a heavy composite,
- introducing **engineered γ‑gradients**:
    - regions with deliberately increased update cost.

---

## 7. Summary

This experiment gives you a concrete, implementable way to:

- contrast brute‑force collisions with engineered pattern composites,
- quantify stability, heaviness, and emergent behavior,
- and build a direct conceptual bridge to real‑world collision experiments.

It is the first step toward a **laboratory for structural physics**, where patterns are not discovered by accident, but **designed on purpose**.
