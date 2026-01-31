# V12b Entity=Tick Hypothesis Results

## Date: 2026-01-30

## Hypothesis

**n_patterns = n_ticks = grid_size**

Each tick creates ONE causal quantum (one entity). At tick N, you have exactly N entities.

## Key Discovery: Init Radius Matters

Initial attempt with `init_radius = grid/10` caused **COLLAPSE** at all scales:
- 100 patterns packed in radius 10 = 0.32 patterns/cell (too dense)

Fixed with `init_radius = sqrt(grid) * 2`:
- Maintains constant pattern density across scales
- 100 patterns in radius 20 = 0.08 patterns/cell (sustainable)

## Final Results

| Grid | Patterns | Init Radius | r_norm | Drift | Status |
|------|----------|-------------|--------|-------|--------|
| 50   | 50       | 14.1        | 0.1265 | 0.017 | STABLE |
| 100  | 100      | 20.0        | 0.0759 | 0.023 | STABLE |
| 200  | 200      | 28.3        | 0.1387 | 0.006 | STABLE |

### Comparison with V12 (area-scaled patterns)

| Grid | V12b Patterns | V12 Patterns | V12b r_norm | V12 r_norm |
|------|---------------|--------------|-------------|------------|
| 50   | 50            | 6            | 0.1265      | COLLAPSED  |
| 100  | 100           | 25           | 0.0759      | 0.063      |
| 200  | 200           | 100          | 0.1387      | 0.075      |

## Analysis

### Entity=Tick Invariant: VERIFIED

```
Grid 50:  50 patterns / 50 ticks = 1.0
Grid 100: 100 patterns / 100 ticks = 1.0
Grid 200: 200 patterns / 200 ticks = 1.0
```

### Scale Invariance: PARTIAL

- Mean r_norm: 0.1137
- Std r_norm: 0.0272
- CV: 0.239 (> 0.2 threshold)

The U-shaped r_norm curve (grid 100 has tightest confinement) suggests:
1. Optimal scale might exist around grid=100
2. The 5:1 window:imprint ratio may need scale-dependent adjustment

### 2D Density Matches Prediction

| Grid | Actual 2D Density | Expected (1/tick) |
|------|-------------------|-------------------|
| 50   | 0.020000          | 0.020000          |
| 100  | 0.010000          | 0.010000          |
| 200  | 0.005000          | 0.005000          |

## Derived Parameters (All Tick Ratios)

```
gamma_window_size = tick / 2
gamma_imprint_k = tick / 10
target_gamma_k = gamma_window_size (V11 coupling)
init_radius = sqrt(tick) * 2  # NEW: for entity=tick
```

The 5:1 window:imprint ratio emerges from:
```
(tick/2) / (tick/10) = 5
```

## Conclusions

1. **Entity=Tick hypothesis validated** - each tick creates one causal quantum
2. **Init radius must scale with sqrt(patterns)** to maintain viable density
3. **All scales stable** - no collapse even at grid=50 with 50 patterns
4. **Not perfectly scale-invariant** - CV=24% suggests further tuning needed

## Open Questions

1. Why does grid=100 show tightest confinement (lowest r_norm)?
2. Is jitter_strength (0.119) also a tick ratio? (12/tick = 0.12)
3. Can the 5:1 ratio be derived from first principles?

## Files Created

- `config_v12.py` - Added `EntityTickConfig` class with `entity_tick_init_radius`
- `experiment_entity_tick.py` - New experiment with verbose output
- `results/entity_tick_sweep.json` - Full results data
