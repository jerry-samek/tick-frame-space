# V6: Dimensional Threshold Unification Experiments

**Date**: 2025-11-18
**Focus**: Testing threshold behavior across 1D-5D to determine if binary threshold collapse is dimension-dependent

---

## Overview

V5 discovered **binary threshold behavior** in 1D: single-source systems require α₀ ≥ 2.00, while multi-source systems (M_s≥2) require only α₀ ≥ 1.00. V6 tests whether this phenomenon persists in higher dimensions or if smooth M_s^(-1/2) scaling emerges.

### Research Questions

1. **H1**: Does binary threshold jump weaken with increasing dimension?
2. **H2**: Do geometry and phase effects emerge for d ≥ 2?
3. **H3**: Does time-dependent threshold persist across dimensions?
4. **H4**: Does threshold scale as α₀ ∝ M_s^(-β(d)) with β(d) approaching 0.5?
5. **H5**: For d ≥ 4, does threshold behavior unify and binary duality disappear?

---

## Experimental Design

### Dimensions Tested

| Dimension | Grid Size | Memory | Expected Runtime |
|-----------|-----------|--------|------------------|
| 1D | 1000 | ~24KB | 5-10 min |
| 2D | 128² | ~400KB | 15-30 min |
| 3D | 64³ | ~6MB | 1-2 hours |
| 4D | 24⁴ | ~8MB | 2-4 hours |
| 5D | 12⁵ | ~6MB | 3-6 hours |

### Parameters

**Fixed across dimensions**:
- Source counts: M_s ∈ {1, 2, 4}
- Geometries: {symmetric, clustered}
- Phase offsets: {0, π} (in-phase, anti-phase)
- Time horizons: T ∈ {100, 200, 500}s
- Damping: γ ∈ {0.001, 0.005}
- Sampling: M = 1

**Swept parameter**:
- Alpha_0: [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]

**Total runs per dimension**: 3 × 2 × 2 × 3 × 2 × 11 = **792 configurations**

---

## Files

### Core Framework
- `dimensional_wave_solver.py` - N-dimensional wave equation solver
  - Arbitrary-dimension Laplacian
  - Adaptive CFL-stable time stepping
  - Gaussian window salience computation

### Dimension-Specific Experiments
- `v6_dimension_1d.py` - 1D sweep (validates against V5)
- `v6_dimension_2d.py` - 2D sweep
- `v6_dimension_3d.py` - 3D sweep
- `v6_dimension_4d.py` - 4D sweep
- `v6_dimension_5d.py` - 5D sweep

### Parallel Execution
- `run_all_dimensions_parallel.py` - Launch all 5 dimensions simultaneously

### Documentation
- `README.md` - This file
- `Dimensional Model Test Plan for Multi-Source Threshold Unification.md` - Original test plan

---

## Running Experiments

### Option 1: Run All Dimensions in Parallel (Recommended)

```bash
cd "W:\foundation\15 experiment\v6"
python run_all_dimensions_parallel.py
```

This launches all 5 dimensions as background processes. Monitor progress:

```bash
# Check log files
tail -f v6_1d_log.txt
tail -f v6_2d_log.txt
# ... etc

# Check running processes
ps aux | grep v6_dimension

# Check for completion (result files)
ls -lh v6_*d_results.csv
```

### Option 2: Run Dimensions Individually

Run one dimension at a time (useful for testing):

```bash
# 1D (fastest, ~10 min)
python v6_dimension_1d.py

# 2D (~30 min)
python v6_dimension_2d.py

# 3D (~2 hours)
python v6_dimension_3d.py

# 4D (~4 hours)
python v6_dimension_4d.py

# 5D (~6 hours)
python v6_dimension_5d.py
```

### Option 3: Background Execution

Run individual dimensions in background:

```bash
# Linux/Mac
nohup python v6_dimension_1d.py > v6_1d_log.txt 2>&1 &
nohup python v6_dimension_2d.py > v6_2d_log.txt 2>&1 &

# Windows (PowerShell)
Start-Process python -ArgumentList "v6_dimension_1d.py" -RedirectStandardOutput "v6_1d_log.txt" -NoNewWindow
```

---

## Expected Outcomes

### Scenario 1: Binary Duality Persists (Null Hypothesis)

If 1D behavior extends to all dimensions:
- **1D-5D**: M_s=1 requires α₀=2.0, M_s≥2 requires α₀=1.0
- **Implication**: Threshold is fundamentally binary, dimension-independent
- **Conclusion**: System has discrete phase transition at M_s=2

### Scenario 2: Smooth Scaling Emerges in 2D+

If higher dimensions show gradual improvement:
- **1D**: Binary (α₀=2.0 vs 1.0)
- **2D**: Partial smoothing (α₀ transitions over M_s=1,2,4)
- **3D+**: Smooth M_s^(-1/2) scaling

**Evidence for smooth scaling**:
- Threshold continuously decreases with M_s
- Geometry effects become measurable (Δα₀ ≥ 0.02)
- Phase effects emerge (in-phase vs anti-phase differs)

### Scenario 3: Dimensional Crossover

If binary → smooth transition occurs at specific dimension:
- **1D**: Binary
- **2D-3D**: Transition regime (partial smoothing)
- **4D-5D**: Unified smooth scaling

**Key indicators**:
- β(d) evolution: measure exponent in α₀ ∝ M_s^(-β(d))
- Geometry sensitivity: Δα₀ (symmetric vs clustered)
- Phase sensitivity: Δα₀ (in-phase vs anti-phase)

---

## Analysis Procedure

After experiments complete, analyze results:

### 1. Threshold Extraction

For each (dimension, M_s, geometry, phase, T, γ):
- Find minimum α₀ with commits
- Report as α₀_threshold

### 2. Scaling Law Fitting

Fit threshold vs source count:
```
α₀_threshold(M_s) = A · M_s^(-β(d))
```

Extract β(d) for each dimension:
- β(1) = ? (expect ~0 if binary)
- β(2) = ?
- β(3) = ?
- β(4) = ?
- β(5) = ? (expect →0.5 if smooth)

### 3. Coherence Detection

**Geometry effect**:
```
Δα₀_geometry = α₀_threshold(clustered) - α₀_threshold(symmetric)
```
Significant if |Δα₀| ≥ 0.02

**Phase effect**:
```
Δα₀_phase = α₀_threshold(anti-phase) - α₀_threshold(in-phase)
```
Significant if |Δα₀| ≥ 0.02

### 4. Dimensional Comparison

Plot:
- α₀_threshold vs M_s for each dimension
- β(d) vs d (scaling exponent evolution)
- Geometry/phase sensitivity vs d
- Time-dependence across dimensions

---

## Output Files

### Per-Dimension Results
- `v6_1d_results.json` / `.csv` - 1D full results
- `v6_2d_results.json` / `.csv` - 2D full results
- `v6_3d_results.json` / `.csv` - 3D full results
- `v6_4d_results.json` / `.csv` - 4D full results
- `v6_5d_results.json` / `.csv` - 5D full results

### Log Files
- `v6_1d_log.txt` - 1D execution log
- `v6_2d_log.txt` - 2D execution log
- `v6_3d_log.txt` - 3D execution log
- `v6_4d_log.txt` - 4D execution log
- `v6_5d_log.txt` - 5D execution log

### Analysis (to be created after experiments)
- `v6_comprehensive_analysis.py` - Cross-dimensional comparison
- `v6_dimensional_comparison_plots.png` - Visualization
- `V6_COMPREHENSIVE_REPORT.md` - Full findings

---

## Expected Timeline

**Parallel execution** (all 5 dimensions):
- Total wall time: ~6 hours (limited by 5D)
- Total CPU time: ~13 hours (sum of all dimensions)

**Sequential execution**:
- 1D: 10 min
- 2D: 30 min
- 3D: 2 hours
- 4D: 4 hours
- 5D: 6 hours
- **Total**: ~13 hours

---

## Troubleshooting

### Memory Issues

If higher dimensions (4D/5D) fail with memory errors:

**Reduce grid size** in respective scripts:
```python
# 4D: reduce from 24⁴ to 20⁴
GRID_SIZE = (20, 20, 20, 20)

# 5D: reduce from 12⁵ to 10⁵
GRID_SIZE = (10, 10, 10, 10, 10)
```

### CFL Violations

Solver uses adaptive time stepping (dt = 0.5 × dx_min / c). If CFL still violated:

**Decrease CFL safety factor** in `dimensional_wave_solver.py`:
```python
dt = 0.4 * dx_min / c  # More conservative (was 0.5)
```

### Long Runtimes

If experiments take too long:

**Reduce parameter space**:
- Fewer alpha_0 values: [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
- Fewer time horizons: [100.0, 500.0]
- Single gamma: [0.001]

**Reduce grid resolution** (less accurate but faster):
- 3D: 48³ instead of 64³
- 4D: 20⁴ instead of 24⁴
- 5D: 10⁵ instead of 12⁵

---

## Next Steps

After V6 completes:

1. **Validate 1D** against V5 results (should match binary threshold)
2. **Analyze scaling** - does β(d) evolve toward 0.5?
3. **Check coherence** - do geometry/phase effects emerge in 2D+?
4. **Unified model** - can we predict threshold in arbitrary dimension?

If dimensional dependence found:
- **V6.1**: Finer dimensional sampling (1.5D? fractal dimensions?)
- **V6.2**: Larger grids for better accuracy
- **V6.3**: Extended parameter space (more M_s values, finer α₀ sweep)

---

## Connection to V1-V5

- **V1-V3**: Established single-source 1D threshold (α₀ ≈ 1.9-2.0)
- **V4**: Discovered time-dependent threshold
- **V5**: Discovered binary multi-source threshold collapse
- **V6**: Tests if collapse is dimension-specific or universal

**Key question**: Is the binary threshold collapse an artifact of 1D geometry, or a fundamental property of the time-visualization model?

---

**Status**: Scripts prepared, ready to launch parallel experiments.
