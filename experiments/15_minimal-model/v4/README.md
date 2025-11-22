# V4 - Extended Time Horizon Analysis

## Overview

Version 4 investigates how the threshold and commit behavior evolve over extended simulation times, testing whether the critical α₀ threshold is time-dependent or invariant.

## V3 Baseline

From v3 ultra-fine sweep (T=100s):
- **Critical threshold**: α₀ ∈ [1.89, 1.90] for γ=0.001, M=1
- **Edge case**: At α₀=1.89, final_Ψ = 1.000108 (99% of threshold, no commits)
- **Onset**: At α₀=1.90, first commit at t=99.1s

---

## V4 Research Questions

### 1. Time-Dependence of Threshold
**Question**: Does the critical α₀ threshold shift with longer simulation time?

**Hypothesis**:
- **Time-invariant**: Threshold stays at [1.89, 1.90] regardless of T
- **Time-dependent**: Threshold decreases with longer T (more time to accumulate)

**Test**: Run T ∈ {100, 200, 500}s with α₀ near threshold

### 2. Commit Saturation
**Question**: Do commits saturate or continue growing with time?

**Metrics**:
- Total commit count vs. T
- Commit rate: dN_commits/dt
- Saturation curve: commits ~ T^β

**Test**: Track commit evolution for α₀ > threshold

### 3. Late-Time Dynamics
**Question**: Does Ψ(t) buildup change character at long times?

**Metrics**:
- Buildup rate: dΨ/dt over time windows
- Salience evolution: S(t) trends
- Energy saturation: max(S) vs. T

---

## Experimental Design

### Test 1: Threshold Stability
**Parameters**:
- α₀ ∈ {1.88, 1.89, 1.90, 1.91, 1.92}
- T ∈ {100, 200, 500}s
- γ = 0.001, M = 1

**Expected outcomes**:
- If time-invariant: Same threshold across all T
- If time-dependent: Threshold decreases with T (e.g., α₀=1.89 commits at T=200s)

### Test 2: Commit Scaling
**Parameters**:
- α₀ ∈ {2.0, 3.0, 5.0, 10.0}
- T ∈ {100, 200, 500}s
- γ = 0.001, M = 1

**Metrics**:
- Total commits vs. T
- Commit rate: N_commits/T
- Scaling exponent: N ~ T^β

### Test 3: Energy Saturation
**Parameters**:
- α₀ ∈ {2.0, 5.0, 10.0}
- T = 500s (extended)
- Track max_salience, avg_salience over time

**Questions**:
- Does artefact field energy saturate?
- Does dΨ/dt decrease at long times?

---

## Implementation Files

### `extended_time_threshold.py`
Tests threshold stability across different simulation times.

### `extended_time_scaling.py`
Analyzes commit count scaling with time.

### `extended_time_dynamics.py`
Tracks long-term Ψ(t) and salience evolution.

### `plot_extended_time_analysis.py`
Generates comprehensive visualizations.

---

## Expected Results

### Scenario A: Time-Invariant Threshold
```
T=100s: threshold at [1.89, 1.90]
T=200s: threshold at [1.89, 1.90]
T=500s: threshold at [1.89, 1.90]
```
**Interpretation**: Threshold is a fundamental property, independent of observation time.

### Scenario B: Time-Dependent Threshold
```
T=100s: threshold at [1.89, 1.90]
T=200s: threshold at [1.87, 1.88]
T=500s: threshold at [1.85, 1.86]
```
**Interpretation**: Longer integration time allows weaker emissions to accumulate past threshold.

### Commit Scaling Predictions

**Linear scaling**: N_commits ~ T (constant commit rate)
**Sublinear scaling**: N_commits ~ T^β, β < 1 (saturation)
**Superlinear scaling**: N_commits ~ T^β, β > 1 (acceleration)

---

## Success Criteria

1. ✅ Determine if threshold is time-invariant (within ±0.01)
2. ✅ Characterize commit scaling law: N(T)
3. ✅ Identify if late-time saturation occurs
4. ✅ Measure long-term buildup dynamics

---

**Version**: 4.0-dev
**Created**: 2025-11-17
**Based on**: v3 ultra-fine threshold analysis
