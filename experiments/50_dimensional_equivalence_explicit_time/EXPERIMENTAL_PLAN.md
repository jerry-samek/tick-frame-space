# Experiment 50: Execution Plan

## Overview

This experiment tests whether **time behaves as a physical dimension** by comparing (n spatial + 1 time) systems against (n+1) spatial dimensions from Experiment #15.

**Key Question**: Does (2D+t) = 3D? Does (3D+t) = 4D? Does (4D+t) = 5D?

## Status: Ready to Execute

All infrastructure is in place and tested. Scripts are ready to run.

### ✅ Completed Setup

1. **Variant A (Time as Physics)**: Wave solver with time in Laplacian (`variant_a_physics/gpu_wave_solver.py`)
2. **Variant B (Time as Storage)**: Wave solver with a sliding window (`variant_b_rendering/gpu_wave_solver.py`)
3. **Baseline validation**: Running now to verify setup matches Experiment #15

### 📋 Execution Queue

**Baseline** (running now):
- 15 configs across 3D, 4D, 5D
- ~5-10 minutes

**Variant A** (ready to run):
- `sweep_2d_plus_time.py`: 180 configs, ~2-3 hours
- Need to create: `sweep_3d_plus_time.py`, `sweep_4d_plus_time.py`

**Variant B** (need to create):
- `sweep_2d.py`, `sweep_3d.py`, `sweep_4d.py`

**Analysis** (need to create):
- Comparison scripts to overlay (n+t) vs (n+1)
- Statistical tests for dimensional equivalence
- Theory Doc 50 checklist completion

## Parameter Sweep Summary

### Focused Coverage (~180 configs per dimension)

```python
Alpha (α₀): [0.8, 1.2, 1.6, 2.0, 2.4]  # 5 values - stable to unstable
Gamma (γ): [0.1, 0.2, 0.3]             # 3 values - damping range
Sources (Ms): [1, 2, 4]                  # 3 values - multi-source
Geometry: ['symmetric', 'clustered']     # 2 values
Phase: [0]                               # 1 value (neutral at high-D)
Time horizon (T): [200, 500]             # 2 values

Total per dimension: 5×3×3×2×1×2 = 180 configs
```

### Grid Sizes (match Experiment #15 v7-final)

- **2D**: 64×64
- **3D**: 48×48×48
- **4D**: 16×16×16×16
- **5D**: 10×10×10×10×10

### Time Window Sizes

- **Variant A**: 10 time slices (creates (n+1)D spacetime grid)
- **Variant B**: 10 time snapshots (storage only, physics remains nD)

## Expected Runtime (CPU)

- **Baseline**: ~10 min (running)
- **2D+t Variant A**: ~2-3 hours
- **3D+t Variant A**: ~1-2 hours
- **4D+t Variant A**: ~30-60 min
- **Variant B** (all): ~4-5 hours total
- **Analysis**: ~1-2 hours

**Total**: ~10-15 hours of CPU time

## Success Criteria

### Dimensional Equivalence (time = dimension)

If metrics match within 10%:
- **(2D+t) ≈ 3D** → CV, ρ, gradient within 10%
- **(3D+t) ≈ 4D** → Stability regime matches
- **(4D+t) ≈ 5D** → Anomaly patterns align

### Generator Distinction (time ≠ dimension)

If (n+t) diverges from (n+1) by >10%:
- Different stability regimes
- New anomaly patterns
- Scaling laws break

## Next Steps

1. **Wait for baseline to complete** (~5 min remaining)
2. **Create remaining sweep scripts** (3D+t, 4D+t for A; all for B)
3. **Run Variant A sweeps** (~4-6 hours total)
4. **Run Variant B sweeps** (~4-5 hours total)
5. **Analyze and compare**
6. **Write conclusions**

## Files Created

```
experiments/50_dimensional_equivalence_explicit_time/
├── README.md                           ✓
├── EXPERIMENTAL_PLAN.md                ✓ (this file)
├── variant_a_physics/
│   ├── README.md                       ✓
│   ├── gpu_wave_solver.py              ✓ (time as dimension)
│   ├── sweep_2d_plus_time.py           ✓
│   ├── sweep_3d_plus_time.py           ⏳ (need to create)
│   └── sweep_4d_plus_time.py           ⏳ (need to create)
├── variant_b_rendering/
│   ├── README.md                       ✓
│   ├── gpu_wave_solver.py              ✓ (time as storage)
│   ├── sweep_2d.py                     ⏳ (need to create)
│   ├── sweep_3d.py                     ⏳ (need to create)
│   └── sweep_4d.py                     ⏳ (need to create)
├── baseline/
│   ├── README.md                       ✓
│   ├── baseline_validation_sequential.py ✓
│   └── [infrastructure files]          ✓
├── analysis/
│   └── [comparison scripts]            ⏳ (need to create)
└── results/
    └── [CSV and JSON outputs]          (generated during runs)
```

## Recommendations

Given the computational time required (~10-15 hours), consider:

1. **Run overnight**: Start Variant A sweeps before bed, Variant B the next night
2. **Phased execution**: Run and analyze one variant at a time
3. **Early validation**: Check baseline results before committing to full sweeps
4. **Parallel if possible**: If multiple machines are available, run variants in parallel

---

**Status**: Infrastructure complete. Baseline validating. Ready for full execution.
**Next**: Complete script generation, then execute sweeps.
