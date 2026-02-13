# Experiment #64 — Three-Body Gravitational Dynamics

**Date**: February 13, 2026
**Status**: PROPOSED
**Substrate**: V18.1 (pressure spreading + fractional accumulator + trilinear interpolation + leapfrog)
**Location**: `experiments/64_three_body/`

---

## Objective

Test whether the existing V18.1 orbital substrate — with zero new code — produces correct three-body gravitational dynamics. This is the first multi-body test of the substrate. All previous orbital validation used one massive central body + test particles. Here, all bodies are dynamically massive and interact mutually through the gamma field.

**Why this matters**: Two-body orbits were the design target. Three-body chaos, ejection dynamics, energy exchange between bodies, and any emergent tangential field asymmetry would be **uninvited results** — physics the substrate produces without being told to.

**Critical reminder**: On this lattice, v = 1 cell/tick = c (speed of light). ALL orbital velocities must be far sub-light. The fractional accumulator handles this — entities accumulate gradient force over many ticks before making integer-cell steps. Typical orbital speeds should be 0.01c–0.05c range.

---

## Substrate Summary (existing, no modifications)

| Component | Mechanism | Parameter |
|-----------|-----------|-----------|
| Field creation | Entity deposits gamma at position each tick | W_center (deposit weight) |
| Field spreading | Pressure equalization to 6 neighbors | fraction = 1/6 (geometric, not tuned) |
| Gradient sampling | Trilinear interpolation at fractional position | Standard particle-mesh |
| Acceleration | Fractional accumulator (fires at threshold ±1.0) | threshold = 1.0 (integer boundary) |
| Integration | Leapfrog (symplectic) | dt = 1 tick |
| Speed limit | |v| ≤ 1 cell/tick = c | Enforced by clipping |

**Zero free parameters** beyond lattice geometry.

---

## Phase 1: Equal-Mass Three-Body Problem

### Setup

Three massive bodies, each formed from a **cluster of stationary depositing entities** (same technique as V18.1 planet formation, but three separate clusters instead of one).

**Grid**: 256×256×256 (need room for ejection)

**Body formation** (each body is a cluster):

| Body | Cluster center | N entities | Cluster radius | Effective mass |
|------|---------------|------------|----------------|----------------|
| A | (88, 128, 128) | 200 | 5 | Equal |
| B | (168, 128, 128) | 200 | 5 | Equal |
| C | (128, 197, 128) | 200 | 5 | Equal |

This places three equal masses in a roughly equilateral triangle configuration, centered on (128, 128, 128), with ~80 cell separation between bodies. The triangle is in the XY plane.

**Formation phase**: 500 ticks with all entities depositing + spreading, no motion. Let the gamma field reach near-equilibrium so each body has a proper 1/r-like hill established.

**Dynamics phase**: Release the cluster centers to move under mutual gravitational influence. Each body's cluster moves as a rigid unit (all entities in a cluster shift together based on the gradient at the cluster center). Track for 20,000 ticks.

**Initial velocities**: ZERO. Let gravity do the work. The three bodies will fall toward their common center of mass and the resulting dynamics will be chaotic.

### Why zero initial velocity?

With zero initial velocity, the system has zero angular momentum. The three bodies fall inward, have a close encounter, and the outcome depends sensitively on the geometry. This is the **Pythagorean three-body problem** — a classic test case with well-known behavior: chaotic exchange, eventual ejection of one body, remaining two form a bound binary.

### Alternative: Finite angular momentum

If zero-velocity produces immediate collision (bodies merge at center), try giving each body a small tangential velocity:

| Body | Initial velocity | Speed |
|------|-----------------|-------|
| A | (0, +0.02, 0) | 0.02c |
| B | (0, -0.02, 0) | 0.02c |
| C | (+0.02, 0, 0) | 0.02c |

This gives nonzero total angular momentum and should produce more complex orbital exchange before ejection. Keep speeds ≪ c.

---

## Phase 2: Asymmetric Mass (Proto-Atomic)

### Setup

One heavy body + two light bodies. This is NOT a real atom (no quantum mechanics, no orbitals). It's the gravitational analog: can two light bodies orbit one heavy body simultaneously, and if so, do they influence each other?

**Grid**: 128×128×128 (lighter bodies stay bound, less room needed)

**Body formation**:

| Body | Type | Cluster center | N entities | Cluster radius |
|------|------|---------------|------------|----------------|
| Nucleus | Heavy | (64, 64, 64) | 700 | 8 |
| Light 1 | Light | (94, 64, 64) | 5 | 1 |
| Light 2 | Light | (64, 94, 64) | 5 | 1 |

**Mass ratio**: 700:5 = 140:1. The nucleus is essentially stationary (center of mass dominated). The two light bodies are at distance 30 from center, 90° apart.

**Initial velocities for light bodies** (tangential, to establish orbits):

| Body | Position offset | Velocity | Speed |
|------|----------------|----------|-------|
| Light 1 | (+30, 0, 0) | (0, +v_orb, 0) | ~0.03c |
| Light 2 | (0, +30, 0) | (-v_orb, 0, 0) | ~0.03c |

**Estimating v_orb**: From V18.1 results, stable orbits at r=30 with 700-entity planet required v ≈ 0.02c–0.05c. Start with v_orb = 0.03 and adjust if needed.

**Formation phase**: 500 ticks, nucleus deposits + spreads, light bodies stationary.

**Dynamics phase**: Release light bodies with tangential velocity. Nucleus cluster stays depositing at center (effectively infinite mass approximation). Track 20,000 ticks.

### Sub-configurations to test:

| Config | Light 1 orbit | Light 2 orbit | Tests |
|--------|--------------|--------------|-------|
| **Co-rotating** | CCW in XY | CCW in XY | Constructive tangential field? |
| **Counter-rotating** | CCW in XY | CW in XY | Destructive tangential field? |
| **Orthogonal** | CCW in XY | CCW in XZ | 3D orbital interaction |
| **Single** | CCW in XY | absent | Control — clean two-body |

---

## Phase 3: Magnetic Emergence Detection

This is the key measurement. Do NOT add any new field or mechanism. Just MEASURE the existing gamma field for tangential asymmetry.

### What to measure

After the light bodies have been orbiting for 5000+ ticks in Phase 2:

1. **Gamma field angular decomposition**: At various radii from the nucleus, decompose the gamma field into radial and tangential components. An orbiting body deposits gamma preferentially along its trajectory — this creates a tangential trail. Measure:
    - Tangential gradient magnitude at r = 20, 25, 30, 35, 40
    - Angular variation of gamma around the orbit plane
    - Fourier modes of the angular distribution

2. **Tangential asymmetry sign**: Does the tangential gradient reverse sign when the orbit direction reverses? Compare co-rotating vs counter-rotating configurations. If the gamma field "remembers" which way the body was going, that's emergent magnetism.

3. **Inter-orbit coupling**: In the two-body case, do the two light bodies affect each other's orbits? Compare:
    - Orbital radius stability: single vs co-rotating vs counter-rotating
    - Orbital period: does it shift with a second body present?
    - Precession: does the orbit plane precess when a second orbiting body is present?

4. **Velocity-dependent deflection test**: Launch a fast test particle (v = 0.1c) through the region around an orbiting body. Does it deflect more than a slow particle (v = 0.01c) at the same impact parameter? Compare with same test through region around stationary nucleus (should be velocity-independent = gravitational).

### Success criteria for magnetic emergence

| Observable | Expected if magnetic | Expected if purely gravitational |
|-----------|---------------------|--------------------------------|
| Tangential asymmetry | Nonzero, sign depends on orbit direction | Zero (symmetric) |
| Co- vs counter-rotating | Different orbital stability | Identical |
| Fast vs slow test particle | Different deflection ratios | Same deflection (or slow > fast) |

If ALL THREE show the magnetic signature, magnetism is emerging from pure orbital dynamics in the gamma field. No signed field, no tang channel, no explicit mechanism. Just entities moving through their own accumulated deposits.

---

## Diagnostics and Output

### Per-tick logging (every 100 ticks):

- Position and velocity of each body center of mass
- Total kinetic energy, total potential energy (from field), total energy
- Angular momentum vector (L_x, L_y, L_z)
- Distance between each pair of bodies
- Maximum gamma value in field

### Trajectory plots:

- 3D trajectory of all bodies (full run)
- Distance vs time for all pairs
- Energy vs time (total, kinetic, potential separately)
- Angular momentum vs time (should be conserved)

### Field snapshots (every 1000 ticks):

- Gamma field slice through orbital plane
- Tangential gradient map at orbital radius
- Radial profile of gamma (azimuthally averaged)

### Phase 1 specific:

- Identify ejection event (one body reaches escape velocity)
- Time to first close encounter
- Final state: binary orbit parameters of remaining pair
- Compare ejection velocity with analytical escape velocity

### Phase 2 specific:

- Orbital elements (a, e, i, Ω, ω) for each light body vs time
- Precession rate
- Tangential field decomposition
- Co-rotating vs counter-rotating comparison

---

## What Each Outcome Means

### Phase 1 (equal-mass three-body):

**If chaotic exchange + ejection occurs with energy conservation**:
→ The substrate correctly handles mutual gravitational interaction from pure gamma deposits. Three-body dynamics emerges uninvited from the two-body substrate. This is strong validation.

**If bodies merge without exchange**:
→ The gamma hills overlap too quickly at these separations. Try larger initial separation (120 cells instead of 80).

**If energy is not conserved (dE/E > 5%)**:
→ The leapfrog integrator has issues with multi-body field evolution. May need to investigate field update timing (spreading interleaved with motion).

**If bodies don't interact (straight-line infall to center)**:
→ The gradient from 200-entity clusters at r=80 is too weak. Increase entity count per cluster or decrease separation.

### Phase 2 (asymmetric mass):

**If two light bodies orbit stably without affecting each other**:
→ The light bodies' gamma deposits are negligible compared to the nucleus. Expected at 700:5 mass ratio. Not wrong, just means the system is effectively two independent two-body problems. Try smaller mass ratio (100:20).

**If the light bodies perturb each other's orbits**:
→ Mutual gravitational interaction between orbiting bodies. Interesting but expected from Newtonian gravity.

**If tangential field asymmetry appears**:
→ **MAJOR RESULT.** Magnetism emerging from pure orbital dynamics. Write it up immediately.

**If tangential field asymmetry does NOT appear**:
→ Either the gamma deposit mechanism doesn't preserve directional information (deposits are symmetric), or the signal is below measurement threshold. Still useful — tells us exactly what the substrate can and cannot produce.

---

## Implementation Notes for Claude Code

### Use existing V18.1 codebase

The substrate is in `experiments/51_emergent_time_dilation/` (likely v13 or v18 subfolder). The key components are:

- Canvas with gamma field + pressure spreading
- Entity motion with fractional accumulator + trilinear interpolation + leapfrog
- Gradient computation

### Moving clusters as rigid bodies

For Phase 1, each "body" is a cluster of entities that should move together. The simplest approach:
- Compute gradient at the cluster's center of mass
- Move ALL entities in the cluster by the same displacement when the accumulator fires
- This treats each cluster as a rigid body

Alternatively, let each entity follow its own gradient — but this might cause clusters to deform. Start with rigid clusters.

### Formation phase is critical

The gamma field must be well-established before dynamics begin. 500 ticks may not be enough for three separate clusters to each develop clean 1/r profiles (recall V18.1 needed many ticks for spreading). Monitor the field profile during formation:
- Does each cluster's field reach the other clusters? (gradient nonzero at neighbor locations)
- Is the combined field roughly what you'd expect from superposition?

If the spreading hasn't reached equilibrium, increase formation ticks to 1000 or 2000.

### Speed calibration

Before the full three-body run, do a quick test: one 200-entity cluster at center, one test particle at r=80 with zero initial velocity. Let it fall. Measure the infall time and maximum velocity reached. This tells you:
- Whether the gradient is strong enough at r=80 (if infall takes >5000 ticks, increase entities)
- Whether the velocity stays sub-light (if it reaches v>0.5c, there's a problem)
- What v_orb should be for Phase 2

### Don't forget: v=1 = c

All velocities in the output should be checked against c. If anything exceeds 0.5c, the dynamics may be unreliable (relativistic effects become important but aren't modeled in the current substrate). The sweet spot is 0.01c–0.1c.

---

## Running

```bash
# Phase 1: Equal-mass three-body (this is the main event)
python experiments/64_three_body/three_body_experiment.py --phase 1

# Phase 2: Asymmetric mass with magnetic detection
python experiments/64_three_body/three_body_experiment.py --phase 2

# Speed calibration (quick sanity check)
python experiments/64_three_body/three_body_experiment.py --calibrate

# Full experiment (all phases)
python experiments/64_three_body/three_body_experiment.py --all
```

Output goes to `experiments/64_three_body/results/`:

- Trajectory plots (3D + projections)
- Energy and angular momentum conservation plots
- Field snapshots at key moments
- Tangential field analysis (Phase 2)
- Summary report with pass/fail criteria
- `experiment_results.json` with all numerical data

---

## Connection to Theory

- **Ch10 §3 (Gamma Attraction)**: Gradient following produces gravity. Three-body extends this to mutual attraction.
- **Ch12 §2-3 (Tangential Curvature)**: Orbiting entities should create tangential deposits. RAW 086: rotation + lag = magnetism.
- **RAW 087 §5 (Lorentz-like effect)**: Velocity-dependent deflection from tangential curvature.
- **Experiment #63**: Validated signed tangential conservation and velocity-dependent deflection in 2D. This experiment tests whether the same physics emerges naturally in 3D from orbital dynamics.

---

## What would be genuinely surprising

1. Three-body chaotic exchange with correct ejection dynamics — uninvited emergence
2. Energy conservation maintained through close encounters — substrate robustness
3. Tangential asymmetry in gamma field around orbiting bodies — emergent magnetism without explicit mechanism
4. Two orbiting bodies with opposite handedness showing different inter-orbit coupling than same-handedness — emergent magnetic interaction
5. Any of the known periodic three-body orbits appearing spontaneously

Any ONE of these would be significant. Multiple would be extraordinary.
