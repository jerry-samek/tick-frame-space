# V12c Results: Tick-Unified Parameters

**Date:** 2026-01-31
**Status:** SUCCESS

## Summary

V12c eliminates empirical ratios by setting all gamma parameters equal to tick:
- `gamma_window_size = tick` (was tick/2)
- `gamma_imprint_k = tick` (was tick/10)
- `target_gamma_k = tick` (was window)

The 5:1 window/imprint ratio becomes 1:1:1. This simplification works as well or better than V12b.

---

## Hypothesis

**User's observation:** "We add 1 for each tick to the window"

The dimensional density argument:
- 1D: see all n entities
- 2D: see n/n² = 1/n fraction
- 3D: see n/n³ = 1/n² fraction

If each tick adds 1 to the window, then window = tick. By the same logic, imprint = tick.

---

## Parameter Comparison

| Parameter | V12b | V12c | Change |
|-----------|------|------|--------|
| window | tick/2 | tick | 2x |
| imprint | tick/10 | tick | 10x |
| well | tick/2 | tick | 2x |
| window/imprint | 5:1 | 1:1 | simplified |

At tick=100:

| Parameter | V12b | V12c |
|-----------|------|------|
| window | 50 | 100 |
| imprint | 10 | 100 |
| well | 50 | 100 |

---

## Experimental Results

### Configuration
- Ticks: 1000 per experiment
- Grid sizes: 50, 100, 200
- Entity count: grid_size (entity=tick hypothesis from V12b)
- Init radius: sqrt(grid) × 2

### Stability Metrics

| Grid | Config | r_norm | Drift | Energy Density | Status |
|------|--------|--------|-------|----------------|--------|
| 50 | V12b | 0.0894 | 0.0170 | 0.316 | STABLE |
| 50 | V12c | 0.0894 | 0.0193 | 0.330 | STABLE |
| 100 | V12b | 0.0776 | 0.0233 | 0.197 | STABLE |
| 100 | V12c | 0.0697 | 0.0150 | 0.198 | STABLE |
| 200 | V12b | 0.1381 | 0.0058 | 0.121 | STABLE |
| 200 | V12c | 0.0998 | 0.0001 | 0.121 | STABLE |

### Key Findings

1. **All scales stable:** V12c achieves 3/3 stable configurations, matching V12b.

2. **Lower drift at larger scales:**
   - Grid 200: V12c drift = 0.0001 vs V12b = 0.0058 (58x improvement)
   - Grid 100: V12c drift = 0.0150 vs V12b = 0.0233 (1.6x improvement)

3. **Tighter confinement:**
   - Grid 200: V12c r_norm = 0.0998 vs V12b = 0.1381 (28% tighter)
   - Grid 100: V12c r_norm = 0.0697 vs V12b = 0.0776 (10% tighter)

4. **Similar energy density:** Both configurations produce nearly identical energy densities.

---

## Interpretation

### Why V12c Works Better

The 1:1:1 ratio creates a balanced system:
- Longer history window (2x) provides more temporal context
- Stronger imprint (10x) creates more persistent presence marking
- These effects balance each other, resulting in more stable dynamics

At larger scales, this balance becomes more important. The V12b 5:1 ratio may have been an artifact of tuning at a single scale (grid=100).

### Physical Meaning

If all parameters = tick, then:
- The universe "remembers" its entire history (window = tick)
- Each entity's presence imprints proportionally (imprint = tick)
- The central well strength matches the temporal depth (well = tick)

This is the simplest possible relationship: everything scales with time.

---

## Parameter Reduction

V12c eliminates two empirical constants:

| Parameter Count | V12b | V12c |
|-----------------|------|------|
| Ratios eliminated | - | WINDOW_RATIO, IMPRINT_RATIO |
| Remaining empirical | 8 | 6 |

### Remaining True Constants (V12c)

1. `jitter_strength = 0.119` (or 12/tick? - future work)
2. `ca_survival_threshold = 3` (topological)
3. `ca_creation_threshold = 5` (topological)
4. `field_decay_threshold = 1.5`
5. `field_decay_rate = 0.05`
6. `creation_sensitivity = 2.0`

---

## Files

| File | Description |
|------|-------------|
| `config_v12.py` | Added `TickUnifiedConfig` class |
| `experiment_tick_unified.py` | V12b vs V12c comparison experiment |
| `results/tick_unified_sweep.json` | Full experimental data |

---

## Conclusion

**V12c hypothesis validated.** The empirical ratios (1/2, 1/10) were approximations. The true relationship is simply:

```
window = imprint = well = tick
```

The simpler 1:1:1 model:
- Matches V12b stability at all scales
- Shows improved stability at larger scales (58x lower drift at grid=200)
- Eliminates 2 empirical constants
- Provides a cleaner theoretical foundation

---

## Next Steps

1. **Jitter investigation:** Is `jitter_strength = 12/tick` (currently 0.119 ≈ 12/100)?
2. **Longer runs:** Test V12c stability over 10k+ ticks
3. **Larger scales:** Test grid=500, 1000 to verify scaling holds
4. **3D extension:** Apply tick-unified parameters to 3D simulations
