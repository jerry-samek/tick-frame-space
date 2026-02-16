# Tick-Frame Physics Quick Reference

**One-page formula sheet and principle summary** | [Full Framework](README.md) | [Glossary](glossary.md)

---

## Core Thesis

> **Time is discrete at the Planck scale and serves as the primary substrate from which space and entities emerge.**

---

## Key Formulas

### Fundamental Constants

```
Planck time:     t_planck = √(ℏG/c⁵) ≈ 5.39×10⁻⁴⁴ s
Planck length:   l_planck = √(ℏG/c³) ≈ 1.62×10⁻³⁵ m
Planck energy:   E_planck = √(ℏc⁵/G) ≈ 1.96×10⁹ J
Speed of light:  c = l_planck / t_planck ≈ 2.998×10⁸ m/s
```

### Tick-Frame Core Equations

| Formula                      | Meaning                        | Chapter        |
|------------------------------|--------------------------------|----------------|
| **1 tick = t_planck**        | Fundamental time quantum       | Ch7 §2         |
| **v_max = c**                | Sample rate limit (structural) | Ch1 §5, Ch7 §2 |
| **E(n) = n × E_tick**        | Energy accumulation            | Ch7 §3         |
| **E(t) = t - t_birth**       | Energy (tick units)            | Ch3 §5         |
| **S ∝ N^ρ**                  | Scaling law                    | Ch2 §3         |
| **ρ_spatial ≈ 1.5**          | Spatial dimension exponent     | Ch2 §3         |
| **ρ_temporal = 2.0**         | Temporal system exponent       | Ch1 §9         |
| **SPBI = (1/CV) × P × 100**  | Dimensional optimality         | Ch2 §3         |
| **State(n+1) = F(State(n))** | Deterministic evolution        | Ch5 §2         |

### Dimensional Scaling

```
CV(d) ≈ 80% × exp(-0.82 × d)    [Coefficient of variation vs dimensions]
SPBI(3D) = 2.23                  [Maximum at 3 dimensions]
```

### Wave Mechanics (Discrete)

```
A(n+1,i) = 2×A(n,i) - A(n-1,i) + [A(n,i+1) - 2×A(n,i) + A(n,i-1)]

ω(k) = (2/Δt) × sin(k×Δx/2)     [Dispersion relation]
f_max = 1/(2×t_planck) ≈ 9.3×10⁴² Hz  [Nyquist limit]
```

### Collision Physics (Exp #55 - January 2026)

```
Pattern = (type, energy, internal_mode, phase, mass)

E_overlap = k_total × sqrt(E_A × E_B)    [Pattern overlap energy]

k_total = weighted_avg(k_type, k_energy, k_mode, k_phase)

Regime Classification:
  - Merge:     E_overlap < E_threshold  →  Fusion (e.g., p + n → D)
  - Explosion: E_overlap > E_max - E_total  →  Annihilation (e.g., e- + e+ → γ)
  - Excitation: Otherwise  →  Redistribution (e.g., p + p → p* + p*)

Emergent Pauli Exclusion:
  If E_total + E_overlap > E_max  →  rejection/excitation (forced to different modes)
```

### Gamma Field Foundations (Ch10-Ch13)

```
Gamma Field:          γ(x, t) — scalar field over discrete lattice, updated each tick
Entity Energy Budget: E_t = E_bind + E_move + E_emit
Gravity (cost grad):  a = -∇C(x)  where C(x) = movement cost at position x
EM Decomposition:     W = W_radial + W_tangential  (gravity + magnetism)
Charge (lag-shear):   Q = handedness of imprint shear (geometric, not intrinsic)
Curvature Duality:    Well ≡ Hill (same geometry, dual interpretation)
Rising Hill:          Entity doesn't climb; hill rises beneath via energy accumulation
Terminal Hill:        Black hole = maximal curvature, perfect coherence, self-sustaining
Existence Condition:  E_bind > E_dissolution  (entity persists iff binding exceeds dissipation)
Cooperation:          N cooperating > N isolated (collective hill-raising is geometrically favored)
```

### Graph-Lattice Gravity (Exp #64_109 v9 - February 2026)

```
Tagged Quanta:
  tagged[eid][node] ∈ int64           [Per-entity integer quanta at each node]
  external_gamma(node, eid) = total[node] - tagged[eid][node]  [Self-subtraction]

Entity Direction:
  internal_direction += (1/mass) * grad_unit   [Continuous 3D nudge]
  normalize(internal_direction)                 [Unit vector]
  hop = argmax(dot(internal_direction, dir_to_neighbor))  [Quantized to k neighbors]

Commit Counter:
  v = c / commit_mass                 [Speed inversely proportional to mass]
  nudge_strength = 1.0 / commit_mass  [Heavier = harder to turn]
```

### Gravitational Time Dilation (Exp #51 v9 - January 2026)

```
∂L/∂t = α∇²L + S(x) - γL²       [Load field diffusion + saturation]
∂E/∂t = R - W(L,E) - D·L        [Energy regeneration + drainage]

γ_grav(x) = f(L(x), E(x))       [Gravitational time dilation from fields]
γ_SR(v) = 1/√(1 - v²/c²)        [Special relativistic factor]

γ_total = γ_grav × γ_SR         [Combined effects - EMERGENT, not programmed!]
```

---

## 7 Gamma Field Principles (from Ch10)

1. **Temporal Surfing**: Entity recreates itself each tick; existence = ongoing process
2. **Gamma Attraction**: Entities cluster inside the field; outside = no gradients = no existence
3. **Existential Drag**: Field interaction imposes cost (drag) but also provides persistence gradients
4. **Rotational Persistence**: Angular momentum as stable imprint mode; rotation resists dissipation
5. **Gamma Slingshot**: Steep gradients can accelerate and redirect entities into new orbits
6. **Existential Boundary**: Outside the gamma field, gradients → 0; leaving = ceasing to exist
7. **Compatibility Maximization**: Entities move/rotate/imprint to maximize signature-field compatibility

---

## 12 Fundamental Principles (from Doc 49)

### Temporal Ontology

1. **Temporal Primacy**: Entities are temporal processes, not objects in time
2. **Tick-Stream Substrate**: Strictly ordered, immutable sequence (tick n → tick n+1)
3. **Existence Buffer**: Finite temporal window (current + past ticks, no future)
4. **Emergent Space**: Space emerges from temporal gradients (not fundamental)
5. **Sample Rate Limit**: v ≤ 1 tick/tick = c (hard physical constraint)
6. **Tick-Rate Limit**: Minimal temporal granularity (representational, not physical)
7. **Causal Readability**: State(n+1) derivable from State(n) (coherence requirement)
8. **Synchrony Requirement**: Observer tick-rate ≥ process tick-rate (stable perception)
9. **Identity Continuity**: Identity = temporal trajectory, not persistent substance
10. **Temporal Aliasing**: Fast processes appear distorted when under-sampled
11. **Temporal Integrity Law**: Valid processes must maintain causality + identity
12. **Observer Dependence**: Perception is sampling-rate dependent

---

## Experimental Validation Summary

### Tier 0: Foundational Properties

| Experiment | Prediction     | Result                 | Status      | Evidence               |
|------------|----------------|------------------------|-------------|------------------------|
| **#15**    | 3D optimal     | SPBI(3D)=2.23 > others | ✓ VALIDATED | 3,960 simulations      |
| **#44**    | v ≤ c enforced | 933× asymmetry         | ✓ VALIDATED | 0% forward, 93% back   |
| **#50**    | ρ=2.0 in (n+t) | ρ=2.000±0.002          | ✓ VALIDATED | 1,095 configs, 0% pass |
| **#46_01** | O(n) bucketing | 2.78× speedup          | ✓ VALIDATED | 297k @ 60 FPS          |

### Tier 1: Physics Mechanisms (January-February 2026)

| Experiment  | Prediction            | Result                                 | Status         |
|-------------|-----------------------|----------------------------------------|----------------|
| **#51 v9**  | Emergent GR+SR        | r ≈ 0.999 correlation                  | ✅ VALIDATED   |
| **#53 v10** | Geodesics (no forces) | 100% orbital success (18/18 entities)  | ✅ VALIDATED   |
| **#55**     | Collision physics     | 6/6 test cases, E_ratio = 1.000        | ✅ VALIDATED   |
| **#55**     | *(Pauli exclusion)*   | Emerged from cell capacity (surprise!) | ✅ **DISCOVERY** |
| **#64_109** | Graph-lattice gravity | Three-body dynamics, exact conservation | ✅ VALIDATED   |
| **#56**     | Composite atoms       | H, He, H₂ structures implemented       | 🔄 In Progress |

**Overall**: 10/11 validations successful (4 Tier 0 + 6 Tier 1). **Two independent gravity implementations converge!**

---

## Falsification Criteria (6 Testable Predictions)

### Observational Physics

1. **Planck-scale dispersion**: High-energy cosmic rays show frequency-dependent speed
2. **Lorentz violation**: Deviations at Planck scale in particle physics

### Computational Physics

3. **3D optimality**: SPBI maximized at d=3 in substrate simulations
4. **Rotation asymmetry**: Forward pitch impossible (0%), backward possible (~93%)
5. **ρ=2.0 signature**: (n+t) systems show quadratic scaling universally
6. **O(n) rendering**: Bucketing outperforms sorting with growing advantage

**Status**: Criteria 3-6 validated computationally. Criteria 1-2 not yet testable (require experiments beyond current
sensitivity).

---

## Entity Dynamics Summary

| Concept              | Formula / Rule                          | Chapter |
|----------------------|-----------------------------------------|---------|
| **Temporal Surfing** | Entity recreates itself each tick       | Ch3 §2  |
| **Energy Growth**    | E = t - t_birth                         | Ch3 §5  |
| **Movement Cost**    | Move when E % momentum.cost == 0        | Ch3 §6  |
| **Division**         | Occurs at E ≥ completeDivisionThreshold | Ch3 §8  |
| **Collision**        | E_merged = E1 + E2 - cost_merge         | Ch3 §7  |
| **Identity**         | UUID + continuous tick presence         | Ch3 §8  |

---

## Observer Model Summary

| Concept           | Definition                               | Chapter |
|-------------------|------------------------------------------|---------|
| **Identity**      | Function: tick n → tick n+1              | Ch4 §2  |
| **Memory**        | Index to historical ticks (not storage)  | Ch4 §3  |
| **Consciousness** | Presence at current tick                 | Ch4 §4  |
| **Sleep**         | Buffer clearing (prevents collapse)      | Ch4 §6  |
| **Perception**    | Selective sampling (tick budget limited) | Ch4 §5  |
| **Trauma**        | High-salience tick (low threshold)       | Ch4 §7  |
| **Déjà vu**       | Index collision (pattern match error)    | Ch4 §7  |
| **Dreams**        | Unconstrained buffer traversal           | Ch4 §7  |

---

## Free Will Framework

| Concept           | Definition                                 | Chapter |
|-------------------|--------------------------------------------|---------|
| **Substrate**     | Fully deterministic (no randomness)        | Ch5 §2  |
| **Frame Level**   | Observers perceive uncertainty (epistemic) | Ch5 §3  |
| **Free Will**     | Auditable agency within causality          | Ch5 §4  |
| **Choice**        | Tick budget allocation                     | Ch5 §5  |
| **Ternary Logic** | {-1, 0, +1} for richer dynamics            | Ch5 §6  |
| **Commit**        | Irreversible, fallible decisions           | Ch5 §8  |

---

## Rendering Performance

| Method      | Complexity     | Performance @ 100k | Max @ 60 FPS       |
|-------------|----------------|--------------------|--------------------|
| Sorting     | O(n log n)     | 14.69 ms           | ~113k entities     |
| Bucketing   | O(n)           | 5.28 ms            | **~297k entities** |
| **Speedup** | **Asymptotic** | **2.78×**          | **2.63× more**     |

**Key Insight**: Discrete time enables O(n) rendering (bucketing by lag) vs O(n log n) sorting by continuous depth.

---

## Implementation Status (Updated January 2026)

### Validated & Implemented ✅

- Temporal ontology (TickTimeConsumer pattern)
- 3D substrate with entity dynamics
- O(n) bucketing (Python experiments)
- Discrete tick evolution
- **Collision physics framework (Exp #55)** - Three regimes, pattern overlap, exact energy conservation
- **Gravitational time dilation (Exp #51 v9)** - Coupled field dynamics, GR+SR combined
- **Geodesic motion (Exp #53 v10)** - Gradient-following, 100% orbital success
- **Graph-lattice gravity (Exp #64_109 v9)** - Self-subtracting tagged quanta, three-body dynamics, exact conservation
- **Composite structures (Exp #56)** - Atoms/molecules with orbital dynamics (validation pending)

### Gaps / In Progress ⚠

- Expansion coupling (λ ≈ 0 currently)
- **Cell capacity E_max universality** - Tested at E_max=20.0, needs broader validation
- Energy balance tracking (feature branch)
- Observer model (not yet implemented)
- **Composite binding validation** - Structures implemented, long-duration stability test pending

### Not Implemented ☐

- Free will / ternary logic (philosophical, no code)
- Sleep mechanism
- Memory indexing
- Length contraction experiment (#54)
- Observer-dependent horizons (#57)

---

## Quick Navigation

### By Topic

- **Foundations**: Ch1 (Temporal Ontology)
- **Dimensions**: Ch2 (Dimensional Framework)
- **Implementation**: Ch3 (Entity Dynamics), Ch6 (Rendering)
- **Philosophy**: Ch4 (Observer), Ch5 (Free Will)
- **Math/Physics**: Ch7 (Formalization)
- **Meta**: Ch8 (Integration & Falsification)
- **Gamma Field**: Ch9 (Furrow/Dark Matter), Ch10 (Foundations), Ch11 (Entity Physics)
- **Curvature/EM**: Ch12 (Electromagnetism & Curvature Geometry)
- **Life/Ontology**: Ch13 (Hill Ontology — Existence to Life)

### By Validation Status

- **Validated**: Ch1, Ch2, Ch6 + Experiments 15, 44, 46_01, 50
- **Partial**: Ch3, Ch7, Ch11 (Exp #51 for gravity, Exp #53 for geodesics)
- **Speculative**: Ch4, Ch5, Ch9, Ch10, Ch12, Ch13

### Key References

- **Smoking Gun**: REFERENCE_doc50_01 (ρ=2.0 signature)
- **Java Basis**: REFERENCE_doc15 (Chapter 15 model)
- **Constitution**: REFERENCE_doc49 (12 principles)
- **Rendering**: REFERENCE_doc46_01 (O(n) validation)

---

## Common Confusions Clarified

### ❌ Time is the 4th dimension

**✓ Correct**: Time is primary substrate; space emerges from it. Dimensionality refers to **spatial dimensions only**. (
n+t) ≠ (n+1) dimensions.

### ❌ Tick-frame is deterministic, so no free will

**✓ Correct**: Free will = auditable agency within determinism, not escape from it. Observers make real choices with
real consequences.

### ❌ Entities exist "between ticks"

**✓ Correct**: Entities only exist AT ticks. Identity is continuity across tick sequence. No continuous existence
between ticks.

### ❌ Bucketing is just an optimization

**✓ Correct**: Bucketing exploits fundamental physical structure (discrete time). It's O(n) because temporal order is
given by physics, not constructed by algorithm.

### ❌ Observers store memories in brain

**✓ Correct**: Brain indexes ticks in existence buffer (pointers), doesn't store experiences (data). Memory =
addressing, not storage.

---

## Research Frontier (Top Open Questions)

### ✅ RECENTLY ANSWERED (January-February 2026)

1. **Gravity mechanism** - ✅ VALIDATED (Exp #51 v9): Coupled field dynamics create emergent GR+SR time dilation (r ≈ 0.999)
2. **Geodesic motion** - ✅ VALIDATED (Exp #53 v10): Objects follow time-flow gradients without force laws (100% orbital success)
3. **Collision physics** - ✅ VALIDATED (Exp #55): Three regimes work, energy conserved exactly
4. **Pauli exclusion** - ✅ DISCOVERED (Exp #55): Emerged from cell capacity limits (NOT predicted!)
5. **Matter-antimatter asymmetry** - ✅ EXPLAINED (Doc 061 + Exp #55): Pattern diversity prevents global annihilation
6. **Graph-lattice gravity** - ✅ VALIDATED (Exp #64_109 v9): Self-subtracting tagged quanta, three-body dynamics, two independent gravity implementations converge!

### 🔥 STILL OPEN (High Priority)

1. **Cell capacity E_max**: Universal constant or scenario-dependent?
2. **Composite binding**: Do γ-wells naturally hold atoms/molecules together? (Exp #56 validation pending)
3. **Lorentz transforms**: Can they be derived from discrete symmetries? (Ch7 §9)
4. **ρ≈1.5 derivation**: Analytical proof from surface-area law + corrections? (Ch7 §6)
5. **Imbalance validation**: Does expansion coupling create predicted asymmetry? (Ch3 §4, Ch8 §4)
6. **QFT formulation**: How to do quantum field theory on tick-lattice? (Ch7 §10)
7. **Gravitational constant G**: Is it derivable from substrate expansion rate λ? (Ch7 §8)
8. **Scalar vs tensor γ-field**: Does EM unification require tensor structure? (Ch10, Ch12)
9. **Well-to-hill transition**: Under what conditions is the hill interpretation required? (Ch12 §6-§10)
10. **Charge quantization**: How does discrete charge arise from lag-flow asymmetry? (Ch12 §4)
11. **Dark matter**: Can gamma-field fossil geometry reproduce rotation curves? (Ch9 §3-§5)

---

## Citation

**Framework**:
> Tick-Frame Physics Theory (Version 2), January 2026.
> https://github.com/your-repo/tick-frame-space
> docs/theory/README.md

**Specific chapters**:
> [Chapter Title], Tick-Frame Physics Theory v2, Ch[N], January 2026.

**Experiments**:
> Experiment #[N]: [Title], [Date]. experiments/[N]_[name]/EXPERIMENT_RESULTS.md

---

**Document Version**: 2.2
**Last Updated**: February 2026
**Status**: Living reference (updates with framework)
**Major Update v2.2**: Added Exp #64_109 (graph-lattice gravity), tagged quanta formulas, updated validation tables
**Major Update v2.1**: Added gamma field formulas (Ch10-Ch13), 7 principles, expanded navigation and open questions
**Major Update v2.0**: Added Tier 1 experimental results (Exp #51, 53, 55, 56), collision physics formulas, gravitational time dilation equations
**Companion Documents**: [README](README.md) | [Glossary](glossary.md) | [Experiment Index](experiment_index.md) | [Honest Status](honest_status.md)
