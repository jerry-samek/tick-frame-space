# v24: Stronger Gradient — M=1000 Star

## Date: March 18, 2026

## Status: Phase 2 running

---

## What v23 Taught Us

v23 ran five distinct configurations across three weeks. The complete arc:

| Run | v_tan | ring_radius | radiate_mass | Best-3 result |
|-----|-------|-------------|--------------|---------------|
| A | 0.00398 | 8 | star=False, disk=True | Escaped tick 36k |
| B | 0.003 | 8 | star=True, disk=True | Bound 60k, late uptick |
| C | 0.003 | 8 | star=False, disk=True | **Best — p8 reversed, p19 locked** |
| D | 0.00394 | 25 | star=False, disk=True | Escaped tick 27k |
| E | 0.003 | 25 | star=False, disk=False | Escaped tick 34k-44k |

**The remaining problem: force strength, not architecture.**

The gradient with M=100 drops off faster than 1/r² and cannot provide sufficient
centripetal force at radii where particles naturally settle (r=20-35).

---

## The Core Insight: The Field Is Too Weak

With M=100 (star_mass=100000), the force measurement at different radii:

| Radius | F_radial | v_circular (i=10) |
|--------|----------|--------------------|
| r=8 | -0.0000198 | 0.00398 |
| r=25 | -0.0000062 | 0.00394 |

The force at r=25 is only 31% of the force at r=8.

**Why M=1000 and not dynamic accretion:**

A dynamic star would introduce four new unknowns. M=1000 is one parameter change
with a known, predictable effect. If the orbit closes with M=1000, the orbital
mechanics are sound. If it still escapes, the problem is in the force law itself.

Add complexity only after the simple version works.

---

## Known Approximations: Float Gamma Field vs Integer Substrate

The current simulation uses `np.float64` for all gamma field values. This is
a continuous approximation of what the true substrate would implement as
discrete integer deposit counts.

### What the simulation does (float approximation)

Each tick the star deposits a continuous amount:

```python
deposited = mass * deposit_rate  # e.g. 1000000 × 1e-5 = 10.0 per tick
```

The spread operation then diffuses gamma fractionally across all neighbors:

```python
outflow = alpha * tagged[bid]        # fraction leaves each node
per_node = outflow / degrees         # split across k neighbors
inflow = A @ per_node               # each neighbor receives 1/k fraction
```

### What the true substrate would do (integer)

In the tick-frame model, gamma is not a continuous fluid. Each deposit event
is one discrete unit at one specific node. There is no diffusion — deposits
spread only by being carried by entities as they hop.

```
True substrate:
  gamma[node] ∈ {0, 1}  — binary: deposit present or absent
  No diffusion operation
  Field spreads only via entity movement at c
```

### The Critical Bound: One Deposit Per Node Maximum

In the true substrate model, a node is a discrete location. It either has a
deposit event or it doesn't. **A single node can hold at most 1 deposit.**

The float gamma field allows unbounded accumulation:
```
M=1,000,000 × deposit_rate=1e-5 = 10 gamma units per tick at one node
```

This is physically impossible in the integer model.

With binary deposits, the force law denominator is bounded:
```
growth = H / (1 + α × 0) = H        (empty node)
growth = H / (1 + α × 1) = H/2      (one deposit, α=1)
```

Maximum suppression factor: 2×. The pathological self-suppression that appears
in v24 (denominator reaching 10,000×) cannot exist in the integer model.
**The anti-Newtonian scaling is a float arithmetic artifact, not physics.**

### Three specific float artifacts

1. **Sub-unit gamma values.** Diffusion produces fractions at distant nodes.
   In the true substrate, nodes have either 0 deposits or 1+ deposits — no fractions.

2. **Instantaneous spread.** Float spread propagates gamma across the entire graph
   in one operation per tick. True substrate spreads only via entity hops at c.

3. **Velocity vectors are visualization-space.** Continuous 3D float vectors derived
   from Euclidean node positions, not integer hop intents per connector.

### Implication for v24

The orbital mechanics results from v24 are valid as a continuum approximation.
If an orbit closes in the float model, it is strong evidence that the underlying
discrete physics supports stable orbits. But the exact orbital parameters will
differ in the true integer substrate implementation.

---

## Why The Star Cannot Be A Point

A real star is not a single node. It is a distributed field accumulated across
billions of atoms, molecules, and nuclear reactions — all carried by entity hops
through many connector chains. The gamma that reaches orbital radius r=8 has
already been distributed, diluted, and re-concentrated across a vast graph volume.

A point star deposits everything at one node, causing:
- Gamma density: M × deposit_rate per tick at one node (unbounded in float model)
- Denominator in force law: 1 + α × (M × deposit_rate) → pathologically large
- Self-suppression so extreme it kills the gradient entirely

A distributed star (body_radius > 0) distributes deposits across ~30-500 nodes:
- Each node accumulates 1/N of the total gamma
- Denominator stays near 1.0
- Gradient propagates cleanly to orbital radii

**v25 direction: distributed star with body_radius = 3-5.**

---

## v24 Architecture: One Change (Star Mass)

All v23 mechanics carry forward unchanged. The only change is star_mass × 10.

### The Change: M=1000

| Parameter | v23 | v24 | Reason |
|-----------|-----|-----|--------|
| star_mass | 100000.0 | **1000000.0** | 10× gradient strength |
| **Everything else** | **unchanged** | **unchanged** | — |

---

## Parameters

| Parameter | v23 | v24 | Reason |
|-----------|-----|-----|--------|
| star_mass | 100000.0 | **1000000.0** | 10× gradient strength |
| n_nodes | 80000 | 80000 | Unchanged |
| radius | 45.0 | 45.0 | Unchanged |
| warm_up | 50000 | 50000 | Unchanged |
| ticks | 60000 | 60000 | Unchanged |
| ring_radius | 8.0 | 8.0 | Start here — natural radius emerges |
| v_tangential | 0.00101 | measured from M=1M field | Anti-Newtonian: weaker than v23 |
| radiate_mass | star=False, disk=False | same | No mass loss on anything |
| deposit_rate | 1e-5 | 1e-5 | Unchanged |
| H | 0.0001 | 0.0001 | Unchanged |
| inertia | 10.0 | 10.0 | Unchanged |
| force_coeff | 1.0 | 1.0 | Unchanged |
| force_interval | 10 | 10 | Unchanged |
| n_ring | 20 | 20 | Unchanged |
| ring_mass | 100.0 | 100.0 | Unchanged |

---

## Phase 1 Results: Anti-Newtonian Scaling

| Metric | v23 (M=100k) | v24 (M=1M) | Ratio |
|--------|-------------|------------|-------|
| F_radial at r=8 | -0.0000198 | -0.00000129 | 0.065× (15× weaker) |
| v_circular (i=10) | 0.00398 | 0.00101 | 0.25× |
| % inward | 100% | 98% | — |

The 10× heavier star produced a 15× weaker force at r=8.

**Explanation:** More mass → 10× more gamma uniformly → denominator 10× larger →
growth 10× smaller. Force comes from asymmetry between connectors, not absolute
growth. Uniform suppression everywhere means no asymmetry means no force.

**This is not a bug.** It is a fundamental property of the float force law:
force saturates and decreases at high gamma density. It is a float arithmetic
artifact — in the true integer model (gamma ∈ {0,1}) this pathological
suppression cannot occur because the denominator is bounded at 2× maximum.

The force and v_circular are internally consistent at the weaker level:
```
Centripetal requirement: 10 × (0.00101)² / 8 = 0.00000128
Measured F_radial: -0.00000129  ✓
```

Phase 2 proceeds with v=0.00101 to test whether orbital mechanics work at
this weaker but internally consistent energy level.

---

## Expected Outcome

### If orbit closes at v=0.00101:
Architecture validated — orbital mechanics work at any consistent force/velocity
combination. The float scaling artifact doesn't prevent orbit formation, it just
shifts the operating point. v25 with distributed star fixes the scaling.

### If orbit still escapes:
The self-suppression is degrading the gradient falloff profile at large radii
(same problem as v23 but worse). The orbit needs correct force law — integer
deposits or distributed star — before it can close.

---

## Success Criteria

### Minimum:
- [ ] r does not reach the graph boundary (r < 50)
- [ ] r decelerates and reverses — at least one radial reversal
- [ ] Reversal amplitude stable or growing slowly

### Intermediate:
- [ ] r oscillates with recognizable perihelion/aphelion
- [ ] Oscillation amplitude stable for 3+ cycles

### Full success:
- [ ] Closed orbit maintained for 10k+ ticks after first full cycle
- [ ] Orbital period measurable and consistent

---

## v25 Direction (Regardless of v24 Outcome)

The v24 result reveals the path forward clearly:

**Fix 1: Distributed star (body_radius = 3-5)**
Eliminates point-star self-suppression artifact. Distributes deposits across
~30-500 nodes. Denominator stays bounded. Force scales correctly with mass.

**Fix 2: Integer gamma field**
Bounds gamma to {0,1} per node. Eliminates ALL self-suppression. Force law
denominator maximum = 2×. Correct substrate physics. Requires replacing
spread() with hop-carried propagation at c.

Fix 1 is simpler and can be done in v25 using existing body_radius parameter.
Fix 2 is the correct theoretical direction but requires significant code changes.

Recommended: v25 = v24 + body_radius=3 for star + re-measure F_radial + Phase 2.

---

## File Structure

```
v24/
  experiment_description.md    (this file)
  results_phase1.md             (detailed phase 1 analysis)
  star_formation.py             (copy of v23/star_formation.py, star_mass=1e6)
  results/
```

---

## References

- v23/experiment_description.md — full v23 arc and conclusions
- v23/star_formation.py — source code to copy
- RAW 112 — The Single Mechanism (binding energy = mass)
- RAW 112 §2.7 — Field self-pinning (denser deposits resist expansion)

---

*Date: March 18, 2026*
*Status: Phase 2 running — v=0.00101 at r=8, radiate_mass=False*
*Predecessor: v23 (dissipative capture, not orbital mechanics)*
*Core change: star_mass × 10 (M=1000) — anti-Newtonian scaling discovered*
*Key finding: force DECREASED 15× with 10× more mass — float self-suppression artifact*
*Key insight: true integer substrate bounds gamma to {0,1} per node — suppression impossible*
*Key insight: point star is physically wrong — real stars distribute deposits across volume*
*v25 direction: distributed star (body_radius=3-5) eliminates self-suppression artifact*
