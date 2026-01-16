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

| Formula | Meaning | Chapter |
|---------|---------|---------|
| **1 tick = t_planck** | Fundamental time quantum | Ch7 §2 |
| **v_max = c** | Sample rate limit (structural) | Ch1 §5, Ch7 §2 |
| **E(n) = n × E_tick** | Energy accumulation | Ch7 §3 |
| **E(t) = t - t_birth** | Energy (tick units) | Ch3 §5 |
| **S ∝ N^ρ** | Scaling law | Ch2 §3 |
| **ρ_spatial ≈ 1.5** | Spatial dimension exponent | Ch2 §3 |
| **ρ_temporal = 2.0** | Temporal system exponent | Ch1 §9 |
| **SPBI = (1/CV) × P × 100** | Dimensional optimality | Ch2 §3 |
| **State(n+1) = F(State(n))** | Deterministic evolution | Ch5 §2 |

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

| Experiment | Prediction | Result | Status | Evidence |
|------------|-----------|--------|--------|----------|
| **#15** | 3D optimal | SPBI(3D)=2.23 > others | ✓ VALIDATED | 3,960 simulations |
| **#44** | v ≤ c enforced | 933× asymmetry | ✓ VALIDATED | 0% forward, 93% back |
| **#50** | ρ=2.0 in (n+t) | ρ=2.000±0.002 | ✓ VALIDATED | 1,095 configs, 0% pass |
| **#46_01** | O(n) bucketing | 2.78× speedup | ✓ VALIDATED | 297k @ 60 FPS |

**Overall**: 4/4 major predictions confirmed in computational experiments

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

**Status**: Criteria 3-6 validated computationally. Criteria 1-2 not yet testable (require experiments beyond current sensitivity).

---

## Entity Dynamics Summary

| Concept | Formula / Rule | Chapter |
|---------|---------------|---------|
| **Temporal Surfing** | Entity recreates itself each tick | Ch3 §2 |
| **Energy Growth** | E = t - t_birth | Ch3 §5 |
| **Movement Cost** | Move when E % momentum.cost == 0 | Ch3 §6 |
| **Division** | Occurs at E ≥ completeDivisionThreshold | Ch3 §8 |
| **Collision** | E_merged = E1 + E2 - cost_merge | Ch3 §7 |
| **Identity** | UUID + continuous tick presence | Ch3 §8 |

---

## Observer Model Summary

| Concept | Definition | Chapter |
|---------|------------|---------|
| **Identity** | Function: tick n → tick n+1 | Ch4 §2 |
| **Memory** | Index to historical ticks (not storage) | Ch4 §3 |
| **Consciousness** | Presence at current tick | Ch4 §4 |
| **Sleep** | Buffer clearing (prevents collapse) | Ch4 §6 |
| **Perception** | Selective sampling (tick budget limited) | Ch4 §5 |
| **Trauma** | High-salience tick (low threshold) | Ch4 §7 |
| **Déjà vu** | Index collision (pattern match error) | Ch4 §7 |
| **Dreams** | Unconstrained buffer traversal | Ch4 §7 |

---

## Free Will Framework

| Concept | Definition | Chapter |
|---------|------------|---------|
| **Substrate** | Fully deterministic (no randomness) | Ch5 §2 |
| **Frame Level** | Observers perceive uncertainty (epistemic) | Ch5 §3 |
| **Free Will** | Auditable agency within causality | Ch5 §4 |
| **Choice** | Tick budget allocation | Ch5 §5 |
| **Ternary Logic** | {-1, 0, +1} for richer dynamics | Ch5 §6 |
| **Commit** | Irreversible, fallible decisions | Ch5 §8 |

---

## Rendering Performance

| Method | Complexity | Performance @ 100k | Max @ 60 FPS |
|--------|-----------|-------------------|--------------|
| Sorting | O(n log n) | 14.69 ms | ~113k entities |
| Bucketing | O(n) | 5.28 ms | **~297k entities** |
| **Speedup** | **Asymptotic** | **2.78×** | **2.63× more** |

**Key Insight**: Discrete time enables O(n) rendering (bucketing by lag) vs O(n log n) sorting by continuous depth.

---

## Implementation Status

### Validated & Implemented ✓
- Temporal ontology (TickTimeConsumer pattern)
- 3D substrate with entity dynamics
- O(n) bucketing (Python experiments)
- Discrete tick evolution

### Gaps / In Progress ⚠
- Expansion coupling (λ ≈ 0 currently)
- Collision dynamics (naive model, full model not active)
- Energy balance tracking (feature branch)
- Observer model (not yet implemented)

### Not Implemented ☐
- Free will / ternary logic (philosophical, no code)
- Sleep mechanism
- Memory indexing
- Relativity compatibility (speculative)

---

## Quick Navigation

### By Topic
- **Foundations**: Ch1 (Temporal Ontology)
- **Dimensions**: Ch2 (Dimensional Framework)
- **Implementation**: Ch3 (Entity Dynamics), Ch6 (Rendering)
- **Philosophy**: Ch4 (Observer), Ch5 (Free Will)
- **Math/Physics**: Ch7 (Formalization)
- **Meta**: Ch8 (Integration & Falsification)

### By Validation Status
- **Validated**: Ch1, Ch2, Ch6 + Experiments 15, 44, 46_01, 50
- **Partial**: Ch3, Ch7
- **Speculative**: Ch4, Ch5

### Key References
- **Smoking Gun**: REFERENCE_doc50_01 (ρ=2.0 signature)
- **Java Basis**: REFERENCE_doc15 (Chapter 15 model)
- **Constitution**: REFERENCE_doc49 (12 principles)
- **Rendering**: REFERENCE_doc46_01 (O(n) validation)

---

## Common Confusions Clarified

### ❌ Time is the 4th dimension
**✓ Correct**: Time is primary substrate; space emerges from it. Dimensionality refers to **spatial dimensions only**. (n+t) ≠ (n+1) dimensions.

### ❌ Tick-frame is deterministic, so no free will
**✓ Correct**: Free will = auditable agency within determinism, not escape from it. Observers make real choices with real consequences.

### ❌ Entities exist "between ticks"
**✓ Correct**: Entities only exist AT ticks. Identity is continuity across tick sequence. No continuous existence between ticks.

### ❌ Bucketing is just an optimization
**✓ Correct**: Bucketing exploits fundamental physical structure (discrete time). It's O(n) because temporal order is given by physics, not constructed by algorithm.

### ❌ Observers store memories in brain
**✓ Correct**: Brain indexes ticks in existence buffer (pointers), doesn't store experiences (data). Memory = addressing, not storage.

---

## Research Frontier (Top Open Questions)

1. **Lorentz transforms**: Can they be derived from discrete symmetries? (Ch7 §9)
2. **ρ≈1.5 derivation**: Analytical proof from surface-area law + corrections? (Ch7 §6)
3. **Imbalance validation**: Does expansion coupling create predicted asymmetry? (Ch3 §4, Ch8 §4)
4. **QFT formulation**: How to do quantum field theory on tick-lattice? (Ch7 §10)
5. **Gravity mechanism**: Is G derivable from substrate expansion rate? (Ch7 §8)

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

**Document Version**: 1.0
**Last Updated**: January 2026
**Status**: Living reference (updates with framework)
**Companion Documents**: [README](README.md) | [Glossary](glossary.md) | [V1→V2 Mapping](v1_to_v2_mapping.md)
