# v7 Follow-Up Experiments Plan

**Based on:** SPBI_EXECUTIVE_SUMMARY.md recommendations
**Parent experiment:** v6-gpu (3,960 runs, 1D-5D)
**Goal:** Investigate saturation boundaries, comparative scaling, and causal structure

---

## Experiment Organization

We **cannot** do all follow-ups in one go due to computational scale:
- Full saturation mapping: 27,720 runs (139 hours for 3D-5D alone)
- Need to split into focused, manageable experiments

---

## v7a - Saturation Boundary Detection

**Priority:** HIGH
**Estimated runs:** ~2,400
**Estimated time:** ~20 hours
**Focus:** Map exact T_sat(γ) boundaries for 3D-5D

### Parameters

```python
dimensions = [3, 4, 5]  # Only dimensions showing saturation
gamma_focused = [0.001, 0.003, 0.005]  # Boundary region
T_extended = [100, 200, 500, 1000, 2000]  # Extended horizon
alpha_0_reduced = [0.8, 1.2, 1.8, 2.4]  # Representative sampling
sources = [2]  # Single representative value (known to be independent)
geometry = ['symmetric']  # Single value (known to be neutral)
phase = [0]  # Single value (known to be neutral)
```

**Runs per dimension:** 3 × 5 × 4 = 60
**Total runs:** 60 × 3 = **180 runs**

**Wait, that's much smaller! Let me recalculate with full params:**

```python
# If we want full parameter coverage at saturation boundary:
gamma_focused = [0.001, 0.003, 0.005]
T_extended = [100, 200, 500, 1000, 2000]
alpha_0_full = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]
sources = [1, 2, 4]
geometry = ['symmetric', 'clustered']
phase = [0, 1]

# Per dimension: 3 × 5 × 11 × 3 × 2 × 2 = 1,980
# Total (3D-5D): 5,940 runs
```

**Recommendation:** Start with reduced parameter set (180 runs) to confirm saturation behavior, then expand if needed.

### Expected Outcomes

1. Identify exact T_sat(γ) for each dimension
2. Confirm saturation cap values (23M, 44M, 111M)
3. Validate γ·T < 1.0 boundary rule
4. Map "Goldilocks zone" precisely

### Artifacts

- `v7a_saturation_3d_results.{csv,json}`
- `v7a_saturation_4d_results.{csv,json}`
- `v7a_saturation_5d_results.{csv,json}`
- `V7A_SATURATION_ANALYSIS.md`
- `saturation_boundaries.png` (γ vs T phase diagram)

---

## v7b - Scale-Normalized Analysis

**Priority:** MEDIUM
**Estimated runs:** 0 (analysis only)
**Estimated time:** ~1 hour
**Focus:** Post-process v6-gpu data with normalized metrics

### Analysis Tasks

1. **Compute CV_norm:**
   ```python
   CV_norm = σ / log(μ + 1)
   ```

2. **Compare discrimination:**
   - Original CV vs CV_norm across dimensions
   - Check if CV_norm provides better separation

3. **Generate comparison plots:**
   - CV vs dimension (original and normalized)
   - SPBI_norm vs dimension

4. **Investigate saturation cap origins:**
   - Code inspection: Check for hard-coded limits
   - Numerical analysis: Test precision boundaries
   - Attractor analysis: Plot convergence trajectories

### Expected Outcomes

1. Determine if CV_norm improves dimensional discrimination
2. Identify source of saturation cap values
3. Recommend metric refinements for future experiments

### Artifacts

- `compute_cv_normalized.py`
- `V7B_NORMALIZED_METRICS.md`
- `cv_comparison.png`
- `saturation_cap_investigation.md`

---

## v7c - Comparative Causal Analysis

**Priority:** MEDIUM
**Estimated runs:** ~500
**Estimated time:** ~4 hours
**Focus:** Compare 3D vs 4D at matched absolute scales

### Strategy

**Problem:** 3D uses 48³ = 110,592 points, 4D uses 16⁴ = 65,536 points

**Solution:** Adjust grid sizes to match:
- **3D:** 48³ = 110,592 points → **baseline**
- **4D:** 18⁴ = 104,976 points → **matched scale**
- **4D (original):** 16⁴ = 65,536 points → **comparison**

### Parameters

```python
dimensions = [
    (3, (48, 48, 48)),      # 110,592 points
    (4, (18, 18, 18, 18)),  # 104,976 points (matched)
    (4, (16, 16, 16, 16))   # 65,536 points (original)
]
gamma = [0.001, 0.005]
T = [100, 200, 500]
alpha_0 = [0.8, 1.2, 1.6, 2.0, 2.4]
sources = [2]  # Known independent
geometry = ['symmetric']  # Known neutral
phase = [0]  # Known neutral
```

**Runs:** 3 configs × 2 × 3 × 5 = **90 runs**

**If full parameter sweep:**
```python
sources = [1, 2, 4]
geometry = ['symmetric', 'clustered']
phase = [0, 1]

# Runs: 3 configs × 2 × 3 × 5 × 3 × 2 × 2 = 1,080 runs
```

**Recommendation:** Start with 90 runs (focused), expand to 1,080 if needed.

### Expected Outcomes

1. Determine if 3D vs 4D differences are purely scale-dependent
2. Test if dimensional phase transition affects causal structure
3. Compare computational efficiency at matched scales

### Artifacts

- `v7c_causal_results.csv`
- `V7C_CAUSAL_COMPARISON.md`
- `scale_matched_comparison.png`

---

## v7d - Ultra-Fine Damping Sweep (Optional)

**Priority:** LOW
**Estimated runs:** ~3,000
**Estimated time:** ~25 hours
**Focus:** Map saturation boundary with precision

### Parameters

```python
dimensions = [3, 4, 5]
gamma_ultrafine = [0.0001, 0.0003, 0.0005, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.008, 0.01]
T = [100, 200, 500, 1000, 2000]
alpha_0 = [1.0, 2.0]  # Representative values
sources = [2]
geometry = ['symmetric']
phase = [0]

# Per dimension: 11 × 5 × 2 = 110
# Total: 330 runs
```

**Note:** Only run if v7a reveals interesting non-linear behavior in saturation boundary.

---

## Execution Recommendations

### Phase 1 (Immediate)
1. **Run v7a (focused)** - 180 runs, ~2 hours
   - Confirms saturation behavior quickly
   - Low risk, high value

2. **Run v7b (analysis)** - 0 runs, ~1 hour
   - No computational cost
   - Validates saturation cap origins
   - Refines metrics

### Phase 2 (If Phase 1 confirms interesting patterns)
3. **Run v7c (focused)** - 90 runs, ~1 hour
   - Tests scale-matching hypothesis

4. **Expand v7a** - Additional 5,760 runs, ~48 hours
   - Full parameter coverage if needed

### Phase 3 (Optional, based on findings)
5. **Run v7d** - 330 runs, ~3 hours
   - Only if saturation boundary shows non-monotonic structure

---

## Summary Table

| Experiment | Runs | Time | Priority | Can Run in Parallel? |
|------------|------|------|----------|---------------------|
| **v7a (focused)** | 180 | 2h | HIGH | Yes (with v7c) |
| **v7a (full)** | 5,940 | 50h | MEDIUM | No (too large) |
| **v7b (analysis)** | 0 | 1h | HIGH | N/A (analysis) |
| **v7c (focused)** | 90 | 1h | MEDIUM | Yes (with v7a) |
| **v7c (full)** | 1,080 | 9h | LOW | Yes (with v7a) |
| **v7d (optional)** | 330 | 3h | LOW | Yes (with others) |

---

## Answer to "Can we do them in one go?"

**Short answer:** No, but we can do v7a (focused) + v7c (focused) + v7b (analysis) in parallel = **270 runs + analysis in ~3 hours total**.

**Long answer:**
- Full saturation mapping (v7a full) is too large (5,940 runs, 50 hours)
- We should start focused (180 + 90 = 270 runs, 3 hours)
- Analyze results, then decide on expansion
- Can run experiments in parallel using separate Python processes

---

## Recommended First Step

**Run combined focused experiment:**

```bash
# Terminal 1: v7a focused (3D)
cd "15 experiment/v7" && python v7a_saturation_3d.py

# Terminal 2: v7a focused (4D)
cd "15 experiment/v7" && python v7a_saturation_4d.py

# Terminal 3: v7a focused (5D)
cd "15 experiment/v7" && python v7a_saturation_5d.py

# Terminal 4: v7c focused
cd "15 experiment/v7" && python v7c_causal_comparison.py

# Total parallel time: ~2 hours (limited by v7a)
```

After completion, run v7b analysis on all results.

---

## Next Actions

1. ✅ Create this plan document
2. ⏳ Create v7a experiment scripts (3D, 4D, 5D)
3. ⏳ Create v7b analysis script
4. ⏳ Create v7c experiment script
5. ⏳ Create shared utilities (copy from v6-gpu)
6. ⏳ Run focused experiments
7. ⏳ Analyze and decide on expansion

---

**Decision point:** Should we prepare focused experiments (270 runs, 3h) or full experiments (7,020 runs, 59h)?
