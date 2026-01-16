# Experiment 50: Dimensional Equivalence Under Explicit Time Dimension

**Test Specification**: Based on `docs/theory/50 Test Specification - Dimensional Equivalence Under Explicit Time Dimension.md`

## Overview

This experiment tests whether the dimensional stability results from Experiment #15 (1D-5D salience field dynamics) remain valid when time is treated as an **explicit dimension** rather than an implicit evolution parameter.

**Research Question**: Does (n spatial dimensions + explicit time) behave like (n+1) spatial dimensions?

## Hypothesis

### If time behaves like a dimension:
- (2D + t) should reproduce (3D) behavior
- (3D + t) should reproduce (4D) behavior
- (4D + t) should reproduce (5D) behavior
- CV, ρ, gradient, salience metrics should align within 10%

### If time is a special generator:
- (n + t) will diverge from (n+1) behavior
- Different stability regimes will emerge
- New anomaly patterns will appear

## Experiment Structure

### Variant A: Time as Physical Dimension (`variant_a_physics/`)
Time is included as a true coordinate dimension in the wave equation Laplacian:
```
∇²A = ∂²A/∂x² + ∂²A/∂y² + ... + ∂²A/∂t²
```
This treats time identically to spatial dimensions at the physics level.

### Variant B: Time as Rendering Dimension (`variant_b_rendering/`)
Time remains a causal evolution parameter in physics but becomes explicit in storage/visualization using the sliding window technique from Experiment #49:
```
buffer[lag][time_offset] = field state
```
This tests whether explicit temporal storage affects dimensional behavior.

### Baseline (`baseline/`)
Quick validation runs from original Experiment #15 (3D, 4D, 5D) to verify our setup matches v6-gpu results.

### Analysis (`analysis/`)
Comparison scripts and statistical tests for (n+t) vs (n+1) dimensional equivalence.

### Results (`results/`)
CSV files, plots, and summary reports.

## Parameter Sweep

**Dimensions Tested**:
- 2D+t, 3D+t, 4D+t (both variants A and B)
- 3D, 4D, 5D (baseline)

**Grid Sizes** (matching Experiment #15 v7-final):
- 2D: 64×64
- 3D: 48×48×48
- 4D: 16×16×16×16
- 5D: 10×10×10×10×10

**Parameters** (~1000 configs per dimension):
- Alpha (α₀): 0.6 to 2.6, 11 steps
- Source count (Ms): 1, 2, 4
- Geometry: symmetric, clustered
- Phase: φ=0, φ=π
- Damping (γ): 0.1, 0.2, 0.3, 0.4
- Time window (W): 5, 10, 20 frames (Variant B only)
- Time horizon (T): 100, 200, 500, 1000

**Total**: ~6000 configurations

## Metrics

All metrics from Experiment #15:
- **CV**: Coefficient of variation (variance/stability)
- **ρ**: Source scaling exponent (independence)
- **Gradient**: Transition sharpness
- **Salience**: Field energy amplification
- **SPBI**: Stability-Probability Balance Index

Plus new temporal metrics:
- Temporal correlation length
- Window size at a stability threshold
- Temporal vs spatial contribution ratio

## Success Criteria

**Dimensional Equivalence** (time = dimension):
- (2D+t) matches 3D within 10%
- (3D+t) matches 4D within 10%
- (4D+t) matches 5D within 10%
- Anomaly patterns align
- Scaling laws hold

**Generator Distinction** (time ≠ dimension):
- Any (n+t) diverges from (n+1) by >10%
- New anomaly classes appear
- Stability regimes shift unexpectedly

## Computational Resources

- **Device**: CPU (Intel ARC GPU not accessible via PyTorch)
- **Estimated Runtime**: 8-10 hours for full sweep
- **Parallel Workers**: 11 (match v7-final)

## Status

**Created**: 2026-01-14
**Completed**: 2026-01-15
**Status**: COMPLETE - GENERATOR DISTINCTION CONFIRMED

**Verdict**: Time is a special generator, not a dimension. All 6 dimensional equivalence tests failed (0/6 passed).

**Key Finding**: Universal ρ=2.0 source scaling signature in all (n+t) systems, contrasting with ρ≈1.5 in pure spatial dimensions.

**Documentation**:
- Local results: `EXPERIMENT_RESULTS.md`
- Theory document: `docs/theory/50_01 Experimental Results - Dimensional Equivalence Rejection.md`
- Test specification: `docs/theory/50 Test Specification - Dimensional Equivalence Under Explicit Time Dimension.md`

## References

- Theory: `docs/theory/50 Test Specification - Dimensional Equivalence Under Explicit Time Dimension.md`
- Base Experiment: `experiments/15_minimal-model/` (especially v6-gpu, v7-final)
- Sliding Window: `experiments/49_sliding_window_rendering/`
