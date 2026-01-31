# V12: Growth Invariance (Tick-Ratio Parameters)

## Core Insight

The tick-stream is the fundamental substrate.

- Each tick adds **1 causal energy quantum**
- Grid grows by **1** each tick (linear, not squared)
- Invariant: `entity_size / tick_stream_size = 1`

The grid is a **projection/visualization** - dimensionality (2D, 3D) is rendering, not physics.

## The Tick-Stream Model

```
tick = N (universal time = substrate size)
grid_size = N (linear growth)
total_energy = N (linear - matches CLAUDE.md)
energy_density = N / N = 1 (constant!)
```

## Parameters as Tick Ratios

### Derived Parameters

| Parameter | Formula | At tick=100 |
|-----------|---------|-------------|
| gamma_window_size | tick / 2 | 50 |
| gamma_imprint_k | tick / 10 | 10.0 |
| target_gamma_k | = window (V11) | 50.0 |

### Emergent Coupling

The "window = 5 × imprint" coupling discovered in V11 is actually:

```
tick/2 = 5 × (tick/10)
```

Both derive from tick - **the coupling emerges naturally from the ratios!**

### Fundamental Ratios (Dimensionless Constants)

| Ratio | Value | Physical Meaning |
|-------|-------|------------------|
| WINDOW_RATIO | 2 | Half of history matters |
| IMPRINT_RATIO | 10 | One-tenth strength imprint |

## Remaining True Constants

After tick-ratio conversion:

| Parameter | Type | Value | Notes |
|-----------|------|-------|-------|
| ca_survival_threshold | Topological | 3 | Discrete (out of 8 neighbors) |
| ca_creation_threshold | Topological | 5 | Discrete (out of 8 neighbors) |
| field_decay_threshold | Unknown | 1.5 | Maybe: 1 + 1/dimension? |
| field_decay_rate | Unknown | 0.05 | Maybe: ~0.5 × jitter? |
| creation_sensitivity | Unknown | 2.0 | Maybe: dimension? |
| jitter_strength | Unknown | 0.119 | Maybe: 12/tick ≈ 0.12? |

## Scale Invariance Test

The key experiment: If parameters as tick-ratios are correct, patterns should be stable at **all scales** with similar **normalized** metrics.

### Test Matrix

| Grid Size | Window | Imprint | Well | Patterns |
|-----------|--------|---------|------|----------|
| 50 | 25 | 5.0 | 25.0 | ~6 |
| 100 | 50 | 10.0 | 50.0 | 25 (baseline) |
| 200 | 100 | 20.0 | 100.0 | 100 |

### Success Criteria

1. **Normalized radius** (r_mean / half_grid) consistent across scales
2. **Energy density** (E / area) consistent across scales
3. **Drift** (normalized) small at all scales

If CV (coefficient of variation) < 15% across scales → **tick-ratio model validated**

## Files

| File | Description |
|------|-------------|
| `config_v12.py` | Tick-ratio config with derived parameters |
| `experiment_scale.py` | Scale invariance test (grid 50, 100, 200) |

## Usage

```bash
# Run default scale sweep (50, 100, 200)
cd experiments/56_composite_objects/v12
python experiment_scale.py

# Single grid test
python experiment_scale.py --grid 100

# Custom grid sizes
python experiment_scale.py --grids "50,100,150,200"

# More ticks for stability
python experiment_scale.py --ticks 5000
```

## Parameter Evolution

| Version | Parameters | Key Reduction |
|---------|------------|---------------|
| V6 | ~12 | Baseline |
| V10 | 9 | Renormalization (decay derived) |
| V11 | 8 | Well=Window coupling |
| V12 | 8 → ? | Tick-ratio derivation |

## Open Questions

1. **Is jitter_strength also a tick ratio?**
   - Current: 0.119
   - Hypothesis: 12/tick = 12/100 = 0.12 (close!)
   - `JitterAsTickRatioConfig` class tests this

2. **Are "fixed game rules" dimension-dependent?**
   - field_decay_threshold = 1.5 → maybe 1 + 1/dim = 1 + 1/2?
   - creation_sensitivity = 2.0 → maybe = dimension?

3. **Why ratios 1/2 and 1/10?**
   - Empirically found, not derived
   - Maybe related to CA thresholds (3/8, 5/8)?

## Conclusion

V12 tests whether the tick-frame model's parameters are **universal ratios** rather than **tuned constants**. If scale invariance holds, we've reduced the parameter space to:

- **2 dimensionless ratios** (1/2, 1/10) - maybe derivable
- **2 topological constants** (CA thresholds 3, 5)
- **~3 unknown constants** (jitter, decay, sensitivity) - may also derive

The ultimate goal: **Zero free parameters** - everything emerges from the tick-stream.
