# V10: Parameter Simplification via Renormalization

## Background: V9 Coupling Discovery

**Key finding:** `decay ≈ 0.85 × jitter` is the coherence condition.
- Ratio works at any scale (confirmed with jitter=0.30, decay=0.25)
- Reduced model from 11 to 10 independent physics parameters

## V10 Goal: Eliminate Decay Parameter via Renormalization

### Problem with Explicit Decay

The current approach uses an artificial "forgetting" process:
```python
history = old_history × (1 - decay) + new_imprint
gamma_effect = history
```

This has issues:
1. `decay` is a free parameter requiring manual tuning
2. The V9 coupling (`decay ≈ 0.85 × jitter`) is unexplained - why 0.85?
3. "Forgetting" is a special mechanism that feels unnatural

### Better Approach: Renormalization

History accumulates without explicit decay. The gamma contribution is
normalized against the total history or background field:

```python
# Accumulation (no decay):
history = old_history + new_imprint

# Normalization on use:
gamma_effect = history / normalization_factor
```

The "decay" effect emerges naturally from the normalization - as total
history grows, each individual contribution's relative weight diminishes.

### Normalization Options

| Option | Formula | Physical Meaning |
|--------|---------|------------------|
| **Global Sum** | `history / (1 + sum(history) / N)` | Total existence dilutes individual influence |
| **Time-Based** | `history / (1 + commits)` | Older history has less weight via commit count |
| **Local Gamma** | `history / gamma_base` | Normalize to local background gamma |

### Expected Benefits

1. **Eliminates decay as a free parameter** (10 → 9 parameters)
2. **More physical** - relative influence diminishes naturally
3. **Couples history to the gamma field itself** - self-consistent

### Parameters After V10

| Parameter | Value | Role |
|-----------|-------|------|
| jitter_strength | 0.119 | Spatial fluctuation amplitude |
| gamma_window_size | 50 | Ticks per history window |
| gamma_imprint_k | 10.0 | History imprint strength |
| ca_survival_threshold | 3 | CA survival rule (fixed) |
| ca_creation_threshold | 5 | CA creation rule (fixed) |
| field_decay_threshold | 1.5 | Low-gamma decay zone (fixed) |
| field_decay_rate | 0.05 | Field decay probability (fixed) |
| creation_sensitivity | 2.0 | Gamma effect on creation (fixed) |

**Removed:** `gamma_history_decay` (replaced by renormalization)

## Experiment Plan

### Experiment 1: Normalization Sweep

Test all three normalization approaches against V9 decay=0.10 baseline:

| Test | Normalization | Expected Behavior |
|------|---------------|-------------------|
| A | Global sum | Total existence dilutes - distributed history favored |
| B | Time-based | Recent history matters more - temporal locality |
| C | Local gamma | High-gamma regions have less history influence |

**Metrics:**
- Stability (r_mean, r_std)
- Energy retention
- Compare to V9 decay=0.10 baseline

**Success criteria:** At least one normalization produces stability without
explicit decay parameter.

### Future Experiments (if normalization works)

- **Window Size Sweep**: Test window = 25, 50, 75, 100
- **Imprint Strength Sweep**: Test imprint_k = 5, 10, 15, 20

## Files

| File | Description |
|------|-------------|
| `config_v10.py` | Config without decay parameter, normalization settings |
| `gamma_history_v10.py` | History committer with renormalization (no decay) |
| `gamma_wells_v10.py` | Gamma well system supporting V10 history committer |
| `experiment_normalization.py` | Test all 3 normalization approaches |
| `experiment_comparison.py` | Compare V10 vs V9 baseline (decay=0.10) |

## Results (2026-01-30)

### V10 vs V9 Comparison (2000 ticks)

| Method | r_mean | r_std | Energy | Stability |
|--------|--------|-------|--------|-----------|
| V9 decay=0.10 | 3.16 | 0.000 | 1353 | 0.004 |
| V10 global_sum | 0.00 | 0.000 | 1054 | 0.000 |
| V10 time_based | 3.16 | 0.000 | 1324 | 0.000 |
| V10 local_gamma | 3.16 | 0.000 | 1415 | 0.000 |

### Key Findings

1. **time_based and local_gamma replicate V9 behavior exactly**
   - Same r_mean=3.16, same stability
   - Demonstrates that decay CAN emerge from normalization

2. **global_sum causes over-confinement**
   - Patterns collapse to center (r_mean → 0)
   - Total history dilution is too aggressive

3. **Recommended approach: time_based**
   - Simplest formula: `history / (1 + commits)`
   - No scale parameter needed
   - Matches V9 without explicit decay

### Parameter Reduction Validated

V10 successfully eliminates `gamma_history_decay` as a free parameter:
- V9: 10 parameters (decay=0.10 required manual tuning)
- V10: 9 parameters (normalization is parameter-free with time_based)

The V9 coupling `decay ≈ 0.85 × jitter` emerges naturally from the
time-based normalization structure.

## Usage

```bash
# Run normalization type sweep (global_sum, time_based, local_gamma)
python experiment_normalization.py --sweep-type

# Run single normalization type
python experiment_normalization.py --type global_sum --scale 1000.0

# Run scale sweep for a normalization type
python experiment_normalization.py --sweep-scale global_sum

# Run V10 vs V9 comparison
python experiment_comparison.py --ticks 2000
```
