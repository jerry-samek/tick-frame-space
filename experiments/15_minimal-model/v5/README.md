# V5: Multi-Source Experiments

**Date**: 2025-11-17
**Focus**: Multi-source emission dynamics, interference, and analytical threshold modeling

---

## Overview

V5 extends the single-source time-visualization model to **multi-source configurations**, exploring how:
- Source count (M_s) affects threshold
- Geometry (symmetric vs asymmetric) influences salience accumulation
- Emission phase creates constructive/destructive interference
- Analytical models can predict threshold behavior

---

## Previous Findings (V1-V4)

### V3 Results (Single Source, T=100s)
- **Threshold**: α₀ ∈ [1.89, 1.90] (±0.01 precision)
- **Optimal parameters**: γ=0.001, M=1
- **Edge case**: α₀=1.89 reaches Ψ=1.000 (99% threshold, no commits)
- **Buildup rate**: dΨ/dt ~ α₀^0.39 (sublinear)

### V4 Results (Extended Time Horizon)
- **Discovery 1**: Threshold is TIME-DEPENDENT
  - T=100s: threshold at [1.89, 1.90]
  - T=200s: threshold at 1.88 (shifted down!)
  - T=500s: threshold at 1.88 (stabilized)

- **Discovery 2**: Commits scale SUPERLINEARLY
  - N ~ T^β where β = 1.8 to 3.5
  - Lower α₀ shows stronger acceleration

---

## V5 Experimental Design

### Core Changes

**Multi-source wave injection**:
```
J(x,t) = Σ qₘ δ(t - tₙ) δ(x - sₘ)
         m=1..M_s
```

**Key modifications**:
- Multiple source positions s₁, s₂, ..., sₘ
- Configurable emission patterns (simultaneous vs phased)
- Energy budget control (total vs per-source amplitude)

---

## Experiments

### Phase A: Geometry and Source Count (`phase_a_geometry_sweep.py`)

**Research questions**:
1. Does threshold scale as α₀_threshold ~ M_s^(-1/2)?
2. Does symmetric vs asymmetric layout matter?
3. How does this interact with time horizon T?

**Parameters**:
- Source counts: M_s ∈ {1, 2, 4, 8}
- Geometries: symmetric, asymmetric
- Alpha_0: [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
- Time horizons: T ∈ {100, 200, 500}s
- Fixed: γ=0.001, M=1

**Expected outcomes**:
- Threshold decreases with more sources (constructive interference)
- Symmetric layout may show lower threshold than asymmetric
- Time-dependence persists across source counts

**Run**:
```bash
python phase_a_geometry_sweep.py
```

**Outputs**:
- `phase_a_geometry_results.json` / `.csv` - Full results
- Threshold scaling analysis
- Geometry comparison

---

### Phase D: Interference and Phase (`phase_d_interference.py`)

**Research questions**:
1. Do in-phase sources create constructive interference (lower threshold)?
2. Do anti-phase sources create destructive interference (higher threshold)?
3. Can we quantify interference factor κ?

**Parameters**:
- Sources: M_s = 2 (symmetric)
- Phase offsets: {0, 1, 2} ticks
  - 0 = simultaneous (in-phase)
  - 1 = alternating (anti-phase)
  - 2 = staggered
- Alpha_0: [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
- Time horizon: T = 200s
- Fixed: γ=0.001, M=1

**Expected outcomes**:
- In-phase (φ=0): lowest threshold (constructive)
- Anti-phase (φ=1): highest threshold (destructive)
- Interference factor κ = α₀_threshold(φ) / α₀_threshold(0)

**Run**:
```bash
python phase_d_interference.py
```

**Outputs**:
- `phase_d_interference_results.json` / `.csv` - Full results
- Interference factor analysis
- Commit count comparison

---

## Analytical Threshold Model

### Hypothesis

From the specification (section 6):

**Effective salience per tick**:
```
S̄ ≈ (M_s / M) · C_eff · (α₀² / γ)
```

**Accumulation over horizon T**:
```
Ψ(T) ≈ S̄ · r_T
```

**Threshold condition**:
```
α₀_threshold(T, γ, M, M_s) ≈ √[(Ψ_th · γ) / (C_eff · M_s/M · r_T)]
```

### Predicted Scaling Laws

1. **Source count**: α₀_threshold ~ M_s^(-1/2)
   - More sources → lower threshold (constructive)

2. **Time horizon**: α₀_threshold ~ T^(-1/2) (early), saturates at long T
   - Matches V4 finding of time-dependent threshold

3. **Damping**: α₀_threshold ~ γ^(1/2)
   - Higher damping → higher threshold

4. **Sampling**: α₀_threshold ~ M^(1/2)
   - Higher M (less frequent sampling) → higher threshold

5. **Interference**: α₀_threshold ~ κ(φ)
   - κ < 1: constructive (in-phase)
   - κ > 1: destructive (anti-phase)

---

## Visualization

**Generate plots**:
```bash
python plot_multi_source_analysis.py
```

**Outputs**:

**Phase A** (`phase_a_comprehensive.png`):
1. Threshold vs source count (onset curves)
2. Threshold scaling law (measured vs theoretical M_s^(-1/2))
3. Symmetric vs asymmetric geometry comparison
4. Commit counts at fixed α₀
5. Time horizon effect
6. Psi accumulation patterns

**Phase D** (`phase_d_interference.png`):
1. Phase effect on threshold (onset curves)
2. Commit counts vs phase offset
3. Commit rate vs phase
4. Interference factor κ summary

---

## Files

### Core Implementation
- `multi_source_simulation.py` - Multi-source simulation framework
  - `MultiSourceConfig` class
  - Geometry builders (symmetric, asymmetric, phased)
  - Wave step with multiple sources
  - Run simulation function

### Experiments
- `phase_a_geometry_sweep.py` - Source count and geometry analysis
- `phase_d_interference.py` - Phase and interference effects

### Analysis
- `plot_multi_source_analysis.py` - Comprehensive visualization
- `Multi-Source Scenario Specification.md` - Theoretical background

---

## Expected V5 Discoveries

Based on the analytical model, we predict:

### 1. Multi-Source Threshold Lowering
- **Single source** (V3): α₀_threshold ≈ 1.90 at T=100s
- **Two sources** (V5): α₀_threshold ≈ 1.90/√2 ≈ **1.34**
- **Four sources** (V5): α₀_threshold ≈ 1.90/√4 ≈ **0.95**

### 2. Geometry Sensitivity
- Symmetric layout: maximum constructive interference
- Asymmetric layout: partial cancellation, higher threshold

### 3. Phase Control
- In-phase (φ=0): strongest constructive, lowest threshold
- Anti-phase (φ=1): partial destructive, higher threshold
- Staggered: intermediate behavior

### 4. Time-Dependence Persists
- Multi-source systems still show threshold shift with T
- Scaling may differ from single-source case

---

## Next Steps

After completing V5 experiments:

1. **Fit analytical model parameters** (C_eff, κ)
   - Extract from Phase A data
   - Validate square-root scaling

2. **Energy budget analysis**
   - Compare: one strong source vs many weak sources
   - Fixed total energy: Σ qₘ = const

3. **Spatial window analysis**
   - Test agent detection window size
   - How does source distance affect salience?

4. **Extended parameter space**
   - Phase B: Dense time sweep T ∈ {100, 200, 300, 500, 800}
   - Phase C: Damping and sampling sweep

---

## Running the Full V5 Suite

```bash
# Phase A: Geometry and source count
python phase_a_geometry_sweep.py

# Phase D: Interference effects
python phase_d_interference.py

# Generate visualizations
python plot_multi_source_analysis.py
```

**Estimated runtime**:
- Phase A: ~15-20 minutes (96 configurations)
- Phase D: ~5 minutes (21 configurations)
- Visualization: <1 minute

**Total data generated**: ~5-10 MB

---

## Key Insights from V5

*(To be filled after experiments complete)*

This section will document:
- Measured threshold scaling vs theoretical prediction
- Geometry effects on interference
- Phase-dependent threshold shifts
- Validation (or revision) of analytical model
- Comparison with single-source V1-V4 findings
