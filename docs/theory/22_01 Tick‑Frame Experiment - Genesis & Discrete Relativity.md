# Tick‑Frame Experiments: Genesis & Discrete Relativity
### *Supplement to Chapter 22 (Genesis) and Chapter 17 (Discrete Relativity)*

This document defines two foundational experiments that extend the tick‑frame universe into:

1. **Genesis simulation** — the discrete Big Bang model
2. **Discrete relativity** — velocity, frames, and causal classification

Both experiments follow the stateless‑substrate model:  
the substrate stores no history; the visualization layer reconstructs all derived quantities.

---

# 1. Genesis Experiment — Discrete Big Bang
### *Primary chapter: 22 — Genesis & Early‑Tick Dynamics*

## Purpose
Model the first ticks of the universe as pure causal spread from a single active site, with:

- no stored history
- no persistent space
- expansion as propagation
- density decay
- horizon growth

This experiment establishes the early‑universe behavior of a stateless substrate.

---

## Substrate Model (Stateless)

### Tick state
A tick contains only the **set of active cells**:

\[
A_t \subset \mathbb{Z}^D
\]

No past states are stored.

### Update rule
Each active cell activates neighbors within radius \(\gamma\):

\[
A_{t+1} = \bigcup_{(x,y)\in A_t} \text{Neighbors}_\gamma(x,y)
\]

This is pure causal spread.

---

## Visualization Layer (Derived Quantities)

The visualization layer reconstructs:

- **Radius:**  
  \[
  r_t = \max_{(x,y)\in A_t} \sqrt{x^2 + y^2}
  \]

- **Active count:**  
  \(|A_t|\)

- **Density:**  
  \[
  \rho_t = \frac{|A_t|}{\text{Volume}(r_t)}
  \]

- **Expected horizon:**  
  \[
  r_{\text{expected}} = \gamma \cdot t
  \]

- **Deviation:**  
  \[
  \Delta r_t = |r_t - \gamma t|
  \]

---

## What to Log

For each tick \(t\):

- tick index
- radius \(r_t\)
- active cell count
- density \(\rho_t\)
- expected horizon radius
- deviation from linear expansion

---

## What This Tests

- Linear horizon growth
- Density decay over ticks
- Early‑tick asymmetry
- Emergence of smooth expansion from discrete rules
- Stateless substrate behavior in the earliest ticks

This experiment forms the empirical backbone of Chapter 22.

---

# 2. Discrete Relativity Experiment — Ticks vs Frames
### *Secondary chapter: 17 — Discrete Relativity & Velocity Constraints*

## Purpose
Demonstrate that:

- velocity is steps/ticks
- timelike/lightlike/forbidden paths emerge naturally
- frame aggregation produces apparent relativistic effects
- no infinities or continuous spacetime are required

This experiment formalizes discrete Lorentz‑like behavior.

---

## Substrate Model (Stateless)

A worldline is a sequence of steps:

\[
s_0, s_1, \ldots, s_{T-1}, \quad s_k \in \{-1,0,+1\}
\]

Position is **not stored**; it is reconstructed:

\[
x(t) = \sum_{k=0}^{t-1} s_k
\]

### Total steps
\[
S = \left|\sum_{k=0}^{T-1} s_k\right|
\]

### True velocity
\[
v = \frac{S}{T}
\]

### Minkowski‑like invariant
\[
s^2 = T^2 - S^2
\]

### Classification
- **Timelike:** \(S < T\)
- **Lightlike:** \(S = T\)
- **Forbidden:** \(S > T\)

This enforces the discrete causal structure.

---

## Visualization Layer — Frame Aggregation

The observer sees frames of size \(F\) ticks.

- Number of frames:  
  \[
  N = \left\lfloor \frac{T}{F} \right\rfloor
  \]

- Apparent frame velocity:  
  \[
  v_{\text{frame}} = \frac{x(t+F) - x(t)}{F}
  \]

Different frame sizes produce different apparent velocities.

---

## What to Log

For each worldline:

- total ticks \(T\)
- total steps \(S\)
- true velocity \(v\)
- classification (timelike/lightlike/forbidden)

For each frame size \(F\):

- number of frames
- average frame velocity
- variance of frame velocities
- cases where motion appears discontinuous (“teleportation”)

---

## What This Tests

- Discrete causal structure
- Forbidden velocities
- Frame‑dependent illusions
- Time dilation as sampling artifact
- Length contraction as reconstruction artifact
- No infinities required

This experiment supports Chapter 17.

---

# Summary

| Experiment | Purpose | Chapter |
|-----------|----------|---------|
| **Genesis** | Early‑tick expansion, density decay, horizon growth | **22** |
| **Discrete Relativity** | Velocity constraints, frame illusions, causal classification | **17** |

Both experiments rely on the stateless substrate model and reinforce the separation between substrate truth and visualization‑layer reconstruction.
