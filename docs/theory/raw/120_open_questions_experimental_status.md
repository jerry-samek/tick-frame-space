# RAW 120: Open Questions and Experimental Status

**Date**: February 20, 2026
**Status**: Working document — consolidates honest open questions from gamma field theory
**Replaces**: Former RAW 120-125, 130, 140, 150, 160, 200, 300 (removed for overreach)

---

## Why This Document Exists

A batch of theoretical documents (RAW 120-300) was written speculatively, attempting to formalize gamma field theory into a complete ontological framework. On review, they contained:
- Bold claims without mathematical backing ("equations unchanged" while introducing custom dynamics)
- Internal contradictions (global field vs causal propagation, continuous substrate vs discrete lattice)
- Concepts disconnected from what experiments actually showed
- Massive duplication across documents

Rather than keep premature formalism, this document records:
1. What experiments have actually demonstrated
2. What honest open questions remain
3. What ideas might be worth revisiting with proper grounding

---

## What Experiments Have Actually Shown

### Gamma Field Gravity (Exp #64_109 v8-v9)
- Integer gamma quanta on a 3D cubic lattice produce attractive force
- Self-subtracting transport: each hop costs 1 quantum from the field → gradient forms
- Three-body dynamics emerge without special-casing
- Force law measured at ~1/r^2.2 (0.2 excess attributable to lattice anisotropy, k=6)

### Macro-Scale Orbits (Exp #64_109 v10)
- 433 stable revolutions at r~2 on a 64K-node lattice (side=40)
- **Key physics insight**: force is turning rate, not acceleration. Speed is constant; gravity rotates the velocity vector between radial and tangential components. This is GR geodesic motion, not Newtonian F=ma.
- Bresenham-like hop accumulator gives infinite angular resolution on a 6-direction lattice
- Gravitational time dilation (variable edge length) required for orbit stability
- Without time dilation: orbits are unstable (inspiral or escape within ~50 ticks)
- Equal-mass case fails: both bodies experience identical gradients, no differential turning

### What Did NOT Work
- Orbit quantization: tested 6 starting separations, only r_start=10 captured. Not quantized like electron shells — just a narrow capture basin near the lattice floor.
- Equal-mass orbits: the gamma field is symmetric, so equal masses see no differential gradient. This is a real limitation, not a parameter tuning issue.
- Conservation laws: energy and angular momentum are approximately conserved but not exactly. No formal conservation proof exists for the discrete system.

---

## Honest Open Questions

### 1. Force Law Convergence
Does the 1/r^2.2 exponent converge to exactly 2.0 as lattice connectivity k increases? The 0.2 excess might be:
- Lattice anisotropy (k=6 cubic lattice is very coarse)
- A genuine deviation from Newton
- An artifact of the measurement method

**What would answer this**: Run v10 on k=12, k=18, k=26 lattices and measure the exponent.

### 2. Conservation Laws
The discrete gamma field does not have a formal conservation law. Energy is approximately conserved in orbits but drifts over long timescales. Questions:
- Is there an exact conserved quantity we haven't identified?
- Is approximate conservation sufficient (like in symplectic integrators)?
- Does the variable edge length (time dilation) introduce or fix energy drift?

**What would answer this**: Long-duration runs with precise energy tracking; analytical work on discrete Noether-like symmetries.

### 3. Equal-Mass Problem
Two equal masses on the gamma lattice see identical, symmetric gradients — no net force differential. This means:
- Binary star systems cannot form in the current model
- The problem might resolve with higher-order gradient effects
- Or it might indicate a fundamental limitation of scalar gamma fields

**What would answer this**: Try vector gamma fields, tensor transport, or explore whether asymmetric initial conditions break the symmetry.

### 4. Composite Object Stability
How do bound states (atoms, molecules) persist on the lattice? Questions:
- What holds a composite together across ticks?
- Is there a minimum mass/energy for stability?
- How does a composite object respond to external gamma gradients?

**What would answer this**: Build multi-node bound states in v10 and test their stability and gravitational response.

### 5. Continuum Limit
The current model is fundamentally discrete (cubic lattice, integer quanta). Does it have a well-defined continuum limit? Specifically:
- Does taking lattice spacing → 0 and quanta → continuous recover smooth GR?
- Is the Bresenham accumulator the correct macro-limit of microscopic dynamics?
- What is the physical meaning of the lattice spacing?

**What would answer this**: Systematic scaling studies; comparison with lattice field theory techniques.

### 6. Photon Ontology
Earlier docs (RAW 065, RAW 081) give contradictory accounts of photons:
- RAW 065: "light IS gamma oscillation" (photon = field mode)
- RAW 081: "photon as degenerate process" (photon = entity at c)

These need reconciliation. v10 doesn't address photons at all — it only has massive bodies.

**What would answer this**: An experiment that tests photon-like entities on the gamma lattice.

### 7. GR Connection — Honest Assessment
v10 shows geodesic-like motion (constant speed, turning = gravity). This is suggestive of GR but:
- We haven't derived the Einstein field equations from gamma dynamics
- The variable edge length was put in by hand, not derived
- We don't know if the model reproduces frame dragging, gravitational waves, or other GR predictions
- The "metric" is just `1 / (1 + alpha * gamma)` — a phenomenological fit, not a derivation

**What would answer this**: Derive the effective metric from first principles; test GR predictions beyond simple orbits.

---

## Ideas Worth Revisiting (With Proper Grounding)

These appeared in the removed documents and might have merit, but need experimental validation before claiming them:

1. **Gamma gradient as curvature**: v10 shows gamma gradients cause turning. Whether this is literally spacetime curvature or just analogous behavior is an open question.

2. **Persistence cost**: The idea that maintaining identity across ticks has an energetic cost. Interesting but undefined — needs a concrete mechanism and testable prediction.

3. **Topological protection of bound states**: The idea that certain configurations are topologically stable. Needs concrete lattice examples, not abstract claims.

4. **Aharonov-Bohm on the lattice**: Path-dependent gamma accumulation could produce AB-like effects. Testable in principle but not yet tested.

---

## What We Should NOT Claim

Based on the review of RAW 120-300, these claims were premature:

- "Equations unchanged" — we have custom dynamics, not standard physics
- "Global geometry" — the field propagates locally, not globally
- "Complete ontological stack" — we have a lattice simulation, not a complete ontology
- "Foundational axioms" — axioms require mathematical rigor we don't have
- "Stationary imprints" — entities move; imprints don't persist stationary
- "Conservation laws" — not demonstrated, only approximate

The right approach: run more experiments, measure more things, let the physics tell us what's true.
