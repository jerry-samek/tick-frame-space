# v7 Follow-Up Experiments

**Parent experiment:** v6-gpu (3,960 runs, 1D-5D)
**Goal:** Investigate saturation boundaries, scale normalization, and comparative causal structure

---

## Experiment Overview

### v7a - Saturation Boundary Detection
**Files:** `v7a_saturation_3d.py`, `v7a_saturation_4d.py`, `v7a_saturation_5d.py`
**Runs:** 60 per dimension (180 total)
**Time:** ~2 hours total (parallelized)

Maps exact T_sat(γ) boundaries for dimensions showing saturation (3D-5D).

**Parameters:**
- γ: [0.001, 0.003, 0.005]
- T: [100, 200, 500, 1000, 2000]
- α₀: [0.8, 1.2, 1.8, 2.4]
- Sources: [2] (known independent)
- Geometry: ['symmetric'] (known neutral)
- Phase: [0] (known neutral)

**Expected outcomes:**
- Identify exact saturation boundaries
- Validate γ·T < 1.0 rule
- Confirm cap values (23M, 44M, 111M)

### v7b - Scale-Normalized Analysis
**File:** `v7b_normalized_analysis.py`
**Runs:** 0 (analysis only)
**Time:** ~1 minute

Post-processes v6-gpu data to compute:
- CV_norm = σ / log(μ + 1)
- CV_log = std(log(x)) / mean(log(x))
- Saturation cap origin investigation

**Expected outcomes:**
- Determine if normalized metrics improve discrimination
- Identify source of saturation cap values
- Confirm caps are natural attractors (not hard-coded)

### v7c - Comparative Causal Analysis
**File:** `v7c_causal_comparison.py`
**Runs:** 90
**Time:** ~1 hour

Compares 3D vs 4D at matched absolute scales:
- 3D: 48³ = 110,592 points (baseline)
- 4D (matched): 18⁴ = 104,976 points
- 4D (original): 16⁴ = 65,536 points

**Expected outcomes:**
- Determine if dimensional differences are scale-dependent
- Test if phase transition affects causal structure
- Compare computational efficiency at matched scales

---

## Quick Start - Focused Experiments

**Recommended approach:** Run all three in parallel for fastest results.

### Option 1: Sequential (safest, ~3 hours total)

```bash
# Terminal 1
cd "W:\foundation\15 experiment\v7"
python v7a_saturation_3d.py
```

Wait for completion, then:

```bash
python v7a_saturation_4d.py
python v7a_saturation_5d.py
python v7c_causal_comparison.py
python v7b_normalized_analysis.py
```

### Option 2: Parallel (fastest, ~2 hours total)

```bash
# Terminal 1 - 3D saturation
cd "W:\foundation\15 experiment\v7"
python v7a_saturation_3d.py

# Terminal 2 - 4D saturation
cd "W:\foundation\15 experiment\v7"
python v7a_saturation_4d.py

# Terminal 3 - 5D saturation
cd "W:\foundation\15 experiment\v7"
python v7a_saturation_5d.py

# Terminal 4 - Causal comparison
cd "W:\foundation\15 experiment\v7"
python v7c_causal_comparison.py
```

After all complete:

```bash
# Any terminal - Analysis
python v7b_normalized_analysis.py
```

**Note:** Running all 4 experiments in parallel will use ~44 workers (4 × 11). Ensure your system can handle the load.

### Option 3: Conservative Parallel (recommended, ~2 hours)

Run only v7a experiments in parallel (33 workers), then v7c separately:

```bash
# Terminals 1-3: Run v7a_saturation_{3d,4d,5d}.py in parallel
# Wait for completion
# Terminal 4: Run v7c_causal_comparison.py
# Terminal 5: Run v7b_normalized_analysis.py
```

---

## Full Parameter Sweep (Optional)

If focused experiments reveal interesting patterns, expand to full parameter coverage.

### v7a Full Parameters

**Edit the scripts** to use:

```python
ALPHA_0_VALUES = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]
NUM_SOURCES_LIST = [1, 2, 4]
GEOMETRIES = ['symmetric', 'clustered']
PHASE_OFFSETS = [0, 1]
```

**Runs per dimension:** 3 × 5 × 11 × 3 × 2 × 2 = 1,980
**Total runs (3D-5D):** 5,940
**Estimated time:** ~50 hours

### v7c Full Parameters

**Edit the script** to use:

```python
NUM_SOURCES_LIST = [1, 2, 4]
GEOMETRIES = ['symmetric', 'clustered']
PHASE_OFFSETS = [0, 1]
```

**Total runs:** 3 configs × 2 × 3 × 5 × 3 × 2 × 2 = 1,080
**Estimated time:** ~9 hours

---

## Expected Output Files

### v7a
- `v7a_saturation_3d_results.{csv,json}`
- `v7a_saturation_4d_results.{csv,json}`
- `v7a_saturation_5d_results.{csv,json}`

### v7b
- `v7b_normalized_metrics.csv`
- `v7b_normalized_comparison.png`

### v7c
- `v7c_causal_comparison_results.{csv,json}`

---

## Analysis Scripts (To Be Created)

After experiments complete, create:

### V7A_SATURATION_ANALYSIS.md
- Saturation boundary plots (γ vs T phase diagrams)
- Exact T_sat(γ) tables
- Cap value validation
- Goldilocks zone mapping

### V7B_NORMALIZED_METRICS.md
- CV discrimination comparison
- Cap origin determination
- Metric recommendation

### V7C_CAUSAL_COMPARISON.md
- Scale-matched comparison
- Dimensional structure vs scale effects
- Computational efficiency analysis

---

## Integration with v6-gpu

All v7 experiments are designed to complement v6-gpu findings:

- **v6-gpu:** Broad parameter sweep across dimensions
- **v7a:** Deep dive into saturation boundaries
- **v7b:** Metric refinement and cap investigation
- **v7c:** Causal structure clarification

---

## Troubleshooting

### Import Errors
Ensure `gpu_wave_solver.py` and `parallel_experiment_runner_adaptive.py` are in the v7 folder:

```bash
cd "W:\foundation\15 experiment\v7"
cp ../v6-gpu/gpu_wave_solver.py .
cp ../v6-gpu/parallel_experiment_runner_adaptive.py .
```

### Memory Issues
Reduce `NUM_WORKERS` in the scripts:

```python
NUM_WORKERS = 6  # Instead of 11
```

### Power/Performance Issues
Run experiments sequentially instead of parallel (Option 1 above).

---

## See Also

- `V7_EXPERIMENT_PLAN.md` - Detailed experimental design
- `../v6-gpu/SPBI_EXECUTIVE_SUMMARY.md` - Motivation for v7 experiments
- `../v6-gpu/DIMENSIONAL_DETERMINISM_EMERGENCE.md` - Background theory

---

**Decision Point:**
- Run **focused experiments** (270 runs, 3h) to validate findings quickly
- Expand to **full experiments** (7,020 runs, 59h) if focused experiments reveal important patterns
