# V5 Preparation Summary

**Date**: 2025-11-18
**Status**: Ready to run experiments

---

## Overview

V5 scenario has been fully prepared to explore **multi-source emission dynamics** and validate the analytical threshold model. All scripts have been implemented and framework-tested successfully.

---

## Files Created

### 1. Core Framework
**`multi_source_simulation.py`** (9.4K)
- `MultiSourceConfig` class for flexible source configurations
- Geometry builders:
  - `create_symmetric_config()` - evenly distributed sources
  - `create_asymmetric_config()` - clustered sources
  - `create_phased_config()` - phase-offset sources
- `run_multi_source_simulation()` - main simulation engine
- Multi-source wave step with summed emissions

**Framework test results**:
```
Single source (α₀=2.0):   1 commit, rate=0.010
Two sources (α₀=1.5):     2 commits, rate=0.020
Four sources (α₀=1.0):    4 commits, rate=0.040
```
✓ Framework working correctly - commit rate scales linearly with source count

### 2. Experiments

**`phase_a_geometry_sweep.py`** (7.7K)
- **Purpose**: Test threshold scaling with source count and geometry
- **Parameters**:
  - Source counts: M_s ∈ {1, 2, 4, 8}
  - Geometries: symmetric, asymmetric
  - Alpha_0: [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
  - Time horizons: T ∈ {100, 200, 500}s
  - Total runs: 96
- **Expected runtime**: 15-20 minutes
- **Outputs**:
  - `phase_a_geometry_results.json`
  - `phase_a_geometry_results.csv`
  - Threshold scaling analysis
  - Geometry comparison tables

**`phase_d_interference.py`** (7.6K)
- **Purpose**: Measure interference effects from emission phase
- **Parameters**:
  - Sources: M_s = 2 (symmetric)
  - Phase offsets: {0, 1, 2} ticks
  - Alpha_0: [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
  - Time horizon: T = 200s
  - Total runs: 21
- **Expected runtime**: 5 minutes
- **Outputs**:
  - `phase_d_interference_results.json`
  - `phase_d_interference_results.csv`
  - Interference factor κ analysis
  - Commit comparison by phase

### 3. Visualization

**`plot_multi_source_analysis.py`** (11K)
- **Phase A plots** (6-panel):
  1. Threshold vs source count (onset curves)
  2. Threshold scaling law (measured vs M_s^(-1/2))
  3. Symmetric vs asymmetric comparison
  4. Commit counts at fixed α₀
  5. Time horizon interaction
  6. Psi accumulation patterns
- **Phase D plots** (4-panel):
  1. Phase effect on threshold
  2. Commit counts vs phase
  3. Commit rate evolution
  4. Interference factor κ
- **Outputs**:
  - `phase_a_comprehensive.png`
  - `phase_d_interference.png`

### 4. Documentation

**`README.md`** (7.2K)
- Complete V5 overview
- Experiment descriptions
- Analytical model summary
- Running instructions
- Expected discoveries

**`Multi-Source Scenario Specification.md`** (3.9K)
- Theoretical foundation (created by user)
- Analytical threshold derivation
- Phase plan (A, B, C, D)

---

## Key Research Questions

### Phase A: Geometry and Source Count
1. **Q1**: Does threshold scale as α₀_threshold ~ M_s^(-1/2)?
   - **Hypothesis**: YES - constructive interference from multiple sources
   - **Prediction**:
     - M_s=1: α₀_threshold ≈ 1.90 (V3 baseline)
     - M_s=2: α₀_threshold ≈ 1.34
     - M_s=4: α₀_threshold ≈ 0.95
     - M_s=8: α₀_threshold ≈ 0.67

2. **Q2**: Does geometry matter?
   - **Hypothesis**: Symmetric shows stronger constructive interference
   - **Prediction**: Asymmetric threshold 5-15% higher than symmetric

3. **Q3**: Time-dependence with multi-source?
   - **Hypothesis**: Time-dependent threshold persists
   - **Prediction**: Threshold shift magnitude may differ from single-source

### Phase D: Interference and Phase
1. **Q4**: Constructive vs destructive interference?
   - **Hypothesis**: In-phase (φ=0) minimizes threshold
   - **Prediction**: Anti-phase (φ=1) raises threshold by 10-30%

2. **Q5**: Quantify interference factor κ?
   - **Hypothesis**: κ = α₀_threshold(φ) / α₀_threshold(0)
   - **Prediction**:
     - φ=0 (in-phase): κ = 1.0 (baseline)
     - φ=1 (anti-phase): κ = 1.2-1.4 (destructive)

---

## Theoretical Predictions

### Analytical Threshold Model

From specification section 6:

```
α₀_threshold(T, γ, M, M_s) ≈ √[(Ψ_th · γ) / (C_eff · M_s/M · r_T)]
```

**Scaling laws**:
- **Source count**: α₀_threshold ∝ M_s^(-1/2)
- **Time horizon**: α₀_threshold ∝ T^(-1/2) (early regime)
- **Damping**: α₀_threshold ∝ γ^(1/2)
- **Sampling**: α₀_threshold ∝ M^(1/2)

### Expected Threshold Values (T=100s, γ=0.001, M=1)

| M_s | Predicted α₀_threshold | Theoretical scaling |
|-----|------------------------|---------------------|
| 1   | 1.90                   | 1.00 × baseline     |
| 2   | 1.34                   | 0.71 × baseline     |
| 4   | 0.95                   | 0.50 × baseline     |
| 8   | 0.67                   | 0.35 × baseline     |

---

## Running the Experiments

### Quick Start

```bash
cd "W:\foundation\15 experiment\v5"

# Phase A: Geometry and source count (15-20 min)
python phase_a_geometry_sweep.py

# Phase D: Interference effects (5 min)
python phase_d_interference.py

# Generate visualizations (<1 min)
python plot_multi_source_analysis.py
```

### Step-by-Step

**1. Phase A experiment**:
```bash
python phase_a_geometry_sweep.py
```
Expected output:
- Console progress report with threshold findings
- `phase_a_geometry_results.json` (detailed)
- `phase_a_geometry_results.csv` (for analysis)
- Threshold scaling table
- Geometry comparison table

**2. Phase D experiment**:
```bash
python phase_d_interference.py
```
Expected output:
- Console progress with phase effect report
- `phase_d_interference_results.json`
- `phase_d_interference_results.csv`
- Interference factor κ table
- Commit rate comparison

**3. Visualization**:
```bash
python plot_multi_source_analysis.py
```
Expected output:
- `phase_a_comprehensive.png` (6 panels)
- `phase_d_interference.png` (4 panels)

---

## Connection to V1-V4

### V1: Initial Threshold Discovery
- Found threshold exists around α₀ ≈ 1.85-1.90
- Precision: ±0.20

### V2: Refined Boundary
- Narrowed to α₀ ∈ [1.85, 1.90]
- Precision: ±0.05
- Tested damping and sampling effects

### V3: Ultra-Fine Resolution
- Pinpointed threshold to [1.89, 1.90]
- Precision: ±0.01
- Discovered edge case: α₀=1.89 reaches 99% threshold
- Characterized buildup dynamics: dΨ/dt ~ α₀^0.39

### V4: Extended Time Horizon
- **Breakthrough 1**: Threshold is TIME-DEPENDENT
  - T=100s: [1.89, 1.90]
  - T≥200s: 1.88
- **Breakthrough 2**: Superlinear commit scaling
  - N ~ T^β where β = 1.8-3.5

### V5: Multi-Source Dynamics (Current)
- **Focus**: How do multiple sources affect threshold?
- **Key addition**: Source count, geometry, and phase control
- **Goal**: Validate analytical model α₀_threshold ~ M_s^(-1/2)

---

## Expected V5 Discoveries

Based on theoretical predictions:

### Discovery 1: Multi-Source Threshold Reduction
**Expected**: Threshold decreases with √M_s
- Validate or refine the M_s^(-1/2) scaling law
- Measure effective interference coefficient C_eff

### Discovery 2: Geometry Sensitivity
**Expected**: Symmetric outperforms asymmetric
- Quantify geometry factor in threshold
- Understand spatial interference patterns

### Discovery 3: Phase-Dependent Interference
**Expected**: In-phase minimizes threshold
- Measure interference factor κ(φ)
- Confirm constructive/destructive behavior

### Discovery 4: Time-Dependence Persists
**Expected**: Multi-source systems show threshold shift with T
- May differ from single-source V4 results
- Test if scaling law holds across time horizons

---

## After V5: Next Steps

Once V5 experiments complete:

1. **Fit analytical model**:
   - Extract C_eff from Phase A data
   - Validate square-root scaling
   - Refine theoretical predictions

2. **Energy budget analysis**:
   - Compare: one strong source vs many weak sources
   - Test energy conservation effects

3. **Phase B: Dense time sweep** (optional):
   - T ∈ {100, 200, 300, 500, 800}s
   - Map α₀_threshold(T) saturation curve

4. **Phase C: Parameter space** (optional):
   - M ∈ {1, 2, 4}, γ ∈ {0.01, 0.005, 0.001}
   - Confirm γ^(1/2) and M^(1/2) scaling

5. **V5 Comprehensive Report**:
   - Document all findings
   - Compare with theoretical predictions
   - Synthesis with V1-V4 results

---

## Summary

✅ **Framework implemented and tested**
✅ **Phase A experiment ready** (96 configurations, ~20 min)
✅ **Phase D experiment ready** (21 configurations, ~5 min)
✅ **Visualization pipeline ready**
✅ **Documentation complete**

**Status**: Ready to run experiments and validate multi-source analytical model.

**Total estimated time**: ~25 minutes for full V5 suite
**Total data**: ~5-10 MB results + visualizations

---

**Next action**: Run `python phase_a_geometry_sweep.py` to begin Phase A experiments.
