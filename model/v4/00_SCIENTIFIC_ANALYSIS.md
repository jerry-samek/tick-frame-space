# Scientific Analysis: RAW Gamma-Field Ontology (Documents 120-300)

## Research Findings for V4 Model Design

**Date:** 2026-02-08
**Context:** Analysis of RAW documents 120-300 to extract implementable physics for the v4 zero-parameter simulation
model.

---

## 1. What RAW Claims To Be

RAW (Reinterpretation of existing Axioms Within) is an **ontological re-parameterization** -- a reinterpretation of what
existing physics equations *mean* at a substrate level. The equations of classical mechanics, quantum mechanics, and
general relativity are preserved; only the metaphysical commitments change.

Central claim: **a single energetic substrate (the gamma field) underlies all physical phenomena**, and
classical/quantum/relativistic physics are different coordinate projections of this substrate.

---

## 2. Architecture: Eight Axioms and Five Layers

### 2.1 Foundational Axioms (RAW 200)

| # | Axiom                                                            | Status                   |
|---|------------------------------------------------------------------|--------------------------|
| 1 | Single continuous global energetic substrate: Gamma(x,t)         | Postulate                |
| 2 | Time is discrete (tick-frame: t -> t+1 -> t+2...)                | Testable in principle    |
| 3 | Entities are stable patterns (imprints) in Gamma, not substances | Philosophical commitment |
| 4 | Existence requires re-instantiation at each tick                 | Core mechanism           |
| 5 | Persistence cost C(x,t) determines re-instantiation              | Central quantity         |
| 6 | Energetic curvature K = nabla^2 C shapes all behavior            | Geometric engine         |
| 7 | Global topology constrains evolution                             | Topological commitment   |
| 8 | Gamma field evolves by symmetry-preserving operator U(Gamma_t)   | Dynamical law            |

### 2.2 Five-Layer Ontological Stack (RAW 300)

```
Layer 5: PHENOMENOLOGICAL  (RAW 120, 121, 130, 140)
         Particles, waves, forces, matter, AB effects
Layer 4: DYNAMIC           (RAW 160)
         Conservation laws from symmetry
Layer 3: GEOMETRIC          (RAW 122, 123, 150)
         Global geometry, geodesics, topology, quantization
Layer 2: PERSISTENCE        (RAW 124, 125)
         Re-instantiation, persistence cost, curvature
Layer 1: SUBSTRATE          (RAW 200 axioms)
         Gamma field, discrete time, imprints
```

---

## 3. The Two Core Innovations

### 3.1 Gravity-Magnetism as Radial/Tangential Curvature (Docs 082-088)

The gamma well decomposes into:

```
W = W_radial + W_tangential
```

- **W_radial** = gravity (isotropic, depends on well depth / mass)
- **W_tangential** = magnetism (anisotropic, depends on rotation + lag)

Three interaction types:

1. Radial-Radial = gravitational attraction
2. Tangential-Tangential = magnetic alignment/repulsion
3. Radial-Tangential coupling = Lorentz force: F_eff = nabla_r W + v x nabla_t W

Charge as lag-flow asymmetry: Q > 0 (clockwise spiral), Q < 0 (counterclockwise), Q = 0 (symmetric).

**Historical comparison:**

- Einstein UFT (1925-55): Failed -- no physical principle, no Maxwell derivation
- Kaluza-Klein (1921): Rigorous 5D derivation of Maxwell, but requires extra dimensions
- Weyl (1918): EM from scale invariance, killed by Einstein's spectral objection
- RAW advantage: No extra dimensions, explicit mechanism (expansion + rotation + lag)
- RAW weakness: Maxwell's equations not formally derived

### 3.2 Photon as Expansion-Carried Imprint (Docs 081, 121, 057, 055)

The reasoning chain:

1. Space expands each tick
2. Entities resist expansion by spending tick budget
3. Photon has zero internal structure (zero tick budget for resistance)
4. Therefore photon is carried by expansion at rate c
5. c = 1 cell/tick = substrate expansion rate
6. Massive entities spend budget on internal complexity -> less speed

**Strengths:** Dissolves wave-particle duality, explains c's observer-independence, explains mass-speed relation.
**Critical gaps:** Dimensional mismatch with H_0, Lorentz invariance in discrete substrate, photon statistics.

---

## 4. Key Resolutions

### 4.1 Weyl's Ghost -- Resolved

Einstein's 1918 objection to Weyl: if EM is geometry, atoms on different paths should show spectral differences.

RAW resolution: EM is **tangential** (anisotropic) curvature; gravity is **radial** (isotropic) curvature. Only
isotropic curvature affects clock rates. Tangential curvature affects directional structure but not temporal flow.
Therefore EM fields don't cause time dilation -- different geometric component entirely.

Additionally: EM is field **modulation** (AC-like), gravity is base curvature (DC-like). Different coupling mechanisms
to atomic structure.

### 4.2 GW170817 -- Resolved

Concern: If substrate c != effective photon c, gravitational waves and light should arrive differently. Constraint:
|v_GW - c|/c < 10^-15.

Resolution: Photon IS a gamma-field pattern, not separate from it. Both gravitational waves and photons propagate as the
same field evolving. Same field, same rate, different geometric modes. The constraint is expected, not problematic.

### 4.3 Hill vs Well Geometry

- **Hill geometry** (entity deposits surplus into field): supports surplus accumulation, cooperative reinforcement,
  life/complexity. Entity creates environment that attracts other entities.
- **Well geometry** (entity drains field): dissipative, entities compete for diminishing resources, no cooperative
  advantage.

V4 implements hill geometry: entities harvest local gamma, keep persistence cost, deposit excess back into field. This
builds hills that create gravitational attraction.

---

## 5. Parameter Reduction Insight

V3 had 25+ free parameters making tuning intractable. The key insight: **all dynamics derive from three structural facts
**:

1. **Hex geometry**: 6 neighbors, diffusion weight = 1/7
2. **c = 1 cell/tick**: movement cost = 1 unit, expansion = 1 unit/tick
3. **Expansion = 1 unit/tick**: the only energy source

Everything else is a geometric consequence:

- Diffusion: (self + 6 neighbors) / 7 -- parameterless
- Harvest: entity absorbs all local gamma -- parameterless
- Persistence cost: 1 unit per cell per tick -- parameterless
- Deposit: all excess returns to field -- parameterless
- Movement: follow gradient, cost = 1 -- parameterless

**Zero physics parameters. Only structural constants: WORLD_RADIUS and seed position.**

---

## 6. V4 Design: The Six Rules

### Rule 1 -- Expansion (energy source)

```
gamma[all_cells] += 1.0
```

### Rule 2 -- Diffusion (field propagation)

```
new_gamma[cell] = (gamma[cell] + sum(gamma[6 neighbors])) / 7
```

### Rule 3 -- Entity Harvest (creates gamma wake)

```
harvest = sum(gamma[entity_cells])
gamma[entity_cells] = 0
```

### Rule 4 -- Persistence Cost

```
cost = len(entity.pattern)
surplus = harvest - cost
entity.energy += surplus
```

### Rule 5 -- Imprinting (builds the hill)

```
reserve = len(entity.pattern)
deposit = max(0, entity.energy - reserve)
gamma[entity_cells] += deposit / len(entity_cells)
entity.energy = min(entity.energy, reserve)
```

### Rule 6 -- Movement (follows gradient)

```
best_direction = argmax(gamma[6 hex neighbors])
if entity.energy >= 1.0:
    move to best_direction
    entity.energy -= 1.0
```

---

## 7. Why This Produces Gravity

1. Entity harvests -> creates local gamma dip (wake)
2. Expansion injects +1 everywhere -> entity cell and neighbors get +1
3. Diffusion: neighbors' higher gamma flows toward entity's dip -> energy funnel
4. Entity harvests again: gets expansion + diffusion inflow > persistence cost -> SURPLUS
5. Entity deposits surplus back -> local gamma RISES above surroundings
6. Net profile: **hill centered on entity**
7. Second entity sees gradient toward first -> moves closer
8. **This is gravitational attraction**

Scaling: In 2D, Green's function ~ log(r) -> gradient ~ 1/r. In 3D (future): ~ 1/r -> gradient ~ 1/r^2 = Newton's
inverse square law.

---

## 8. Critical Open Questions

### Tier 1 -- Show-stoppers if not resolved:

1. Derive Maxwell's equations from gamma-field dynamics
2. Address coupling constant hierarchy (G vs e^2 ratio of 10^36)
3. Formal proof that tangential curvature produces zero clock-rate contribution

### Tier 2 -- Major gaps:

4. Gauge invariance (where is U(1)?)
5. Strong and weak nuclear forces (SU(3), SU(2))
6. Spin and fermion statistics
7. Photon statistics (Bose-Einstein)

### Tier 3 -- Refinements:

8. First-order vs second-order dynamics tension
9. Dimensional analysis of persistence cost
10. Formal update operator specification
11. Lorentz invariance preservation in discrete substrate

---

## 9. V4 Success Criteria

Phase 1 is validated if:

1. Single entity accumulates energy over time (surplus > 0)
2. Visible dip-then-hill profile around entity
3. Two entities drift toward each other (gravitational attraction)
4. Entity accumulates enough surplus to replicate
5. Paired entities accumulate surplus faster than isolated ones
6. Entity in depleted region loses cells and dissolves
7. **No free parameters were needed**
