# Experiment 56 V4: Running Instructions (Updated After Runaway)

## What Happened with 100 Fragments

The initial run with 100 fragments **entered catastrophic runaway mode** starting around tick 70,000:

- Cloud radius exploded: 2.0 → 19,333 (10,000× expansion)
- 70 out of 100 fragments escaped
- Energy went positive (unbound state)
- Root cause: **Energy pumping exceeded dissipation**

### Why It Failed

With 100 fragments sharing the same total mass (0.1):
- Each fragment: 0.001 mass (was 0.002 with 50 fragments)
- Jitter strength: 0.001 (unchanged)
- **Jitter-to-mass ratio doubled**: 1.00 vs 0.50
- **Energy injection increased 4×**: System pumped energy faster than collisions could dissipate it
- Collisions (restitution=0.8) remove only 20% per collision → insufficient

## Updated Configuration: Back to Proven Baseline

**RECOMMENDED**: Use `ultra_long` configuration
- **50 fragments** (V3 proven baseline)
- **200k ticks** (2× longer than V3 for better quantization)
- Same physics parameters that worked in V3

This configuration:
- ✓ Proven stable (V3: 3.43% drift, 0 escapes over 100k ticks)
- ✓ Longer duration allows full equilibration
- ✓ Addresses V3's 23% energy drift issue
- ✓ Better chance for quantization emergence

## How to Run

Navigate to the v4 directory:
```bash
cd experiments/56_composite_objects/v4
```

Run with the recommended configuration (now the default):
```bash
python experiment_56a_v4_quantization.py
```

Or explicitly specify:
```bash
python experiment_56a_v4_quantization.py ultra_long
```

## Available Configurations

| Config Name | Fragments | Ticks | Runtime | Status |
|-------------|-----------|-------|---------|--------|
| `quantization` | 50 | 100k | ~7 min | ✓ V3 validated (3.43% drift) |
| `high_resolution` | 100 | 100k | ~7 min | ? Untested (may runaway) |
| **`ultra_long`** | **50** | **200k** | **~15 min** | **✓ RECOMMENDED** |
| `high_res_ultra_long` | 100 | 200k | ~15 min | ✗ FAILED (runaway at 70k) |

## Expected Runtime

**~15 minutes** for the recommended `ultra_long` configuration

The simulation will print progress updates every 1,000 ticks showing:
- Progress percentage (0.0% → 100.0%)
- Elapsed time and ETA
- Cloud radius (should stay near r ≈ 2.0)
- Kinetic/potential/total energy
- Angular momentum
- Collision statistics
- Fragment escape warnings (should be 0)

## What to Look For

### Stability Indicators (Good Signs)
- **Cloud radius**: Should stabilize around r ≈ 2.0 ± 0.2
- **Energy conservation**: E_total should stabilize after initial thermalization
- **No escapes**: All 50 fragments should remain bound
- **Collision rate**: ~5-10 collisions/tick (indicates active thermalization)
- **Angular momentum**: Should gradually converge to stable value

### Warning Signs (If These Appear, Stop the Run)
- Cloud radius growing continuously (r > 4.0)
- Energy drift accelerating (not stabilizing)
- Fragments escaping (any escapes in first 50k ticks is bad)
- Collision rate dropping to near zero
- Cloud collapsing (r < 0.5)

## What Changed from V3

**V3 (baseline)**:
- 50 fragments, 100k ticks
- Result: Stable, 3 radial shells detected
- Issue: 23% energy drift, angular momentum not converged

**V4 ultra_long (this run)**:
- 50 fragments, **200k ticks** (2× longer)
- Expected: Same stability, better equilibration
- Goal: Energy conservation < 5%, angular momentum convergence, energy gaps

## Theoretical Context

This experiment tests **Doc 070_01 §4 Quantization Hypothesis**:
> "Collision dynamics naturally drive the system toward stable orbital levels, quantized energy states, and robust equilibrium distributions."

**Previous results**:
- V3 (100k ticks): **3 radial shells** detected ✓, but no energy gaps or L quantization
- V4 (100k ticks, 100 fragments): **Runaway** ✗

**Current hypothesis**:
- 50 fragments is the natural stable count for this binding energy
- 200k ticks needed for full quantization emergence
- Energy gaps and L quantization require longer equilibration than shells

## After Completion

Results will be saved to:
```
results/exp56a_v4_50frags_200k.json
```

### Expected Quantization Signatures

Based on V3 success + longer duration:

1. **Radial Shells** (VERY LIKELY): 3+ discrete peaks in ρ(r)
   - V3 found 3 shells at r = [0.3, 0.9, 1.9]
   - Longer run should make these even more pronounced

2. **Energy Level Gaps** (POSSIBLE): Forbidden energy regions
   - V3 didn't show this in 100k ticks
   - May emerge after full equilibration (>150k ticks?)

3. **Maxwell-Boltzmann Distribution** (LIKELY): Thermal equilibrium
   - Collision thermalization should produce MB velocity distribution
   - Confirms system reached equilibrium

4. **Angular Momentum Quantization** (POSSIBLE): L_z convergence
   - V3: L_z = -0.00267 with σ = 0.001 (still evolving)
   - 200k ticks may allow convergence to stable quantized value

### Analysis

Run the analysis script (if you prepared one) or manually check:
```python
import json
data = json.load(open('results/exp56a_v4_50frags_200k.json'))
```

Key metrics to extract:
- Final cloud radius vs initial (drift %)
- Energy conservation (E_final - E_initial) / |E_initial|
- Fragment escapes
- Radial shell structure (from detailed snapshots)
- Energy histogram (check for gaps)
- Angular momentum convergence (rolling std)

## If This Configuration Also Fails

**Fallback plan**: Extend to 3D implementation

Per your guidance: "If it fails, we will try our luck with 3d"

**Why 3D might help**:
- Theory (Doc 015_01) suggests 3D is minimum realistic dimension
- 3D has full angular momentum vector (not just scalar L_z)
- Different collision phase space
- More realistic atomic physics

**Next steps if runaway occurs**:
1. Document the failure mode
2. Compare 2D vs 3D physics differences
3. Implement 3D version of fragmented cloud
4. Re-run with same parameters in 3D

---

## Quick Start Commands

```bash
# Navigate to v4 directory
cd experiments/56_composite_objects/v4

# Run recommended configuration (50 fragments, 200k ticks)
python experiment_56a_v4_quantization.py

# Monitor output for stability indicators
# Expected runtime: ~15 minutes
# Watch for "SUCCESS" message at end
```

**Ready to run!** The proven V3 baseline + extended duration should give us stable quantization data.
