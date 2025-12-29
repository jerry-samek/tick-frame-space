# Experiment v2 - Full Observatory Guide

## Overview

**File:** `run_full_experiment_v2.py`

This is the comprehensive experiment runner that includes:
- ✅ **8 observers** (all except pi_drift)
- ✅ **Pre-observation simulation** (configurable T_unseen)
- ✅ **Energy model presets** (cold/warm/hot/extreme)
- ✅ **Small-world initial state** (20 entities, Watts-Strogatz topology)

## Active Observers

| Observer | Tracks | Output File |
|----------|--------|-------------|
| **Genesis** | Entities, edges, horizon, branching | `genesis_metrics.csv` |
| **Constants Drift** | alpha, G, h, Lambda | `constants_drift.csv` |
| **Relativity** | Time dilation, velocity effects | `relativity_metrics.csv` |
| **Entropy** | Graph disorder | `entropy_metrics.csv` |
| **Particle** | Collision dynamics | `particle_metrics.csv` |
| **Force Collapse** | Clustering forces | `force_collapse_metrics.csv` |
| **Horizon** | Causal boundaries from root | `horizon_metrics.csv` |
| **Warp** | Spacetime curvature around center | `warp_metrics.csv` |

## Energy Model Presets

### COLD START (Default immediately observable universe)
```python
energy_config = cold_start
```
- **T_unseen**: 0 ticks
- **E0**: 0 (no energy)
- **Behavior**: Stable constants, slow growth, equilibrium dynamics

### WARM START (Currently selected)
```python
energy_config = warm_start
```
- **T_unseen**: 1000 ticks
- **E0**: 1000 (moderate energy)
- **tau**: 10 (cooling timescale)
- **Behavior**: Initial energy boost, gradual cooling, moderate constant drift

### HOT START
```python
energy_config = hot_start
```
- **T_unseen**: 5000 ticks
- **E0**: 25,000 (high energy!)
- **tau**: 5 (fast cooling)
- **Behavior**: Explosive early dynamics, rapid constant changes, settles to equilibrium

### EXTREME START
```python
energy_config = extreme_start
```
- **T_unseen**: 10,000 ticks
- **E0**: 100,000 (extreme energy!)
- **tau**: 5 (fast cooling)
- **Behavior**: Chaotic early phase, dramatic constant drift, long cooling period

## How to Use

### 1. Select Energy Configuration

Edit line ~100 in `run_full_experiment_v2.py`:

```python
# Choose one:
energy_config = warm_start   # <-- Change this
config_name = "WARM START"   # <-- Update name to match
```

### 2. Adjust Parameters (Optional)

**Max ticks:**
```python
MAX_TICKS = 10000  # Increase for longer runs
```

**Log interval:**
```python
LOG_INTERVAL = 10  # Log every N ticks (10 = 1000 entries for 10k ticks)
```

**Base dynamics:**
```python
base_params = {
    'base_birth': 0.05,    # Birth rate
    'base_expand': 0.15,   # Edge expansion
    'base_decay': 0.15,    # Edge decay
    'base_rewire': 0.10,   # Edge rewiring
    'base_bias': 0.10,     # Preferential attachment
}
```

### 3. Run Experiment

```bash
cd experiments/22_genesis-and-discreet-relativity/v1
python run_full_experiment_v2.py
```

### 4. Analyze Results

All CSV files will be in `results/` directory.

## Expected Behaviors by Configuration

### COLD START (E = 0)

**Constants:**
- alpha: Stabilizes at ~0.96
- G: Increases to 1.0 (perfect clustering)
- h: Collapses to 0 (isolated nodes)
- Lambda: Decays to 0 (no expansion)

**Genesis:**
- Slow entity growth (~0.05 per tick)
- Moderate edge growth
- Dense local clusters

**Outcome:** Boring equilibrium (heat death)

---

### WARM START (E0 = 1000, tau = 10)

**Energy decay:**
- Tick 1: E = 1000
- Tick 10: E = 368
- Tick 100: E = 0.045
- Tick 1000: E ≈ 0

**Constants:**
- alpha: Early volatility (0.5-1.0), then stabilizes
- G: Gradual increase to 1.0
- h: Fluctuates wildly early, settles later
- Lambda: Spikes to ~0.5 initially, decays to 0

**Genesis:**
- Rapid early growth (birth_prob × 1000 initially!)
- Explosive edge formation
- Gradual slowdown as energy decays

**Outcome:** Phase transition from chaos (hot) to order (cold)

---

### HOT START (E0 = 25000, tau = 5)

**Energy decay (very fast):**
- Tick 1: E = 25000
- Tick 5: E = 9196
- Tick 10: E = 3368
- Tick 50: E = 0.68
- Tick 100: E ≈ 0

**Constants:**
- alpha: **Wild oscillations** (0.2-1.0) in first 50 ticks
- G: Drops initially (network too chaotic), then recovers
- h: Extreme spikes (0-200+)
- Lambda: **Massive spike** (5+ entities/tick!), rapid decay

**Genesis:**
- **Explosive birth** (hundreds of entities in first ticks)
- **Runaway edge growth** (thousands of edges immediately)
- Rapid collapse to equilibrium

**Outcome:** Big Bang → rapid cooling → equilibrium

---

### EXTREME START (E0 = 100000, tau = 5)

**Energy decay:**
- Tick 1: E = 100000
- Tick 5: E = 36788
- Tick 10: E = 13534
- Tick 100: E = 0.005

**Constants:**
- **Completely chaotic** for first 100 ticks
- All constants show maximum variance
- Possible network collapse/fragmentation

**Genesis:**
- **Thousands of entities** created in first ticks
- **Tens of thousands of edges**
- May hit performance/memory limits

**Outcome:** Extremely hot Big Bang, possible substrate breakdown

---

## Understanding Energy Effects

**Energy multipliers on probabilities:**

| Probability | Formula | Cold (E=0) | Warm (E=1000) | Hot (E=25000) |
|-------------|---------|------------|---------------|---------------|
| **expand** | `base × (1 + E)` | 0.15 | 150.15 | 3750.15 |
| **decay** | `base × (1 + 1/(1+E))` | 0.30 | 0.15 | 0.15 |
| **birth** | `base × (1 + E)` | 0.05 | 50.05 | 1250.05 |
| **bias** | `base × (1 + E)` | 0.10 | 100.10 | 2500.10 |

**Key insight:** At high E, birth/expand/bias become **massive**, while decay stays controlled.

Result: **Explosive growth** that cools down as E decays.

## Comparing Configurations

Run the same experiment with different energy configs and compare:

**Files to compare:**
- `constants_drift.csv` - Do constants stabilize at same values?
- `genesis_metrics.csv` - Does final state depend on initial energy?
- `entropy_metrics.csv` - Does disorder follow same trajectory?

**Hypothesis (Tick-Frame theory):**
- **If constants are emergent:** Different T_unseen → different final constants
- **If constants are fundamental:** Same final constants regardless of T_unseen

## Recommendations

### For Testing Emergent Constants

1. Run **COLD START** (baseline)
2. Run **WARM START** (moderate energy)
3. Run **HOT START** (high energy)
4. Compare final constant values (last 1000 ticks)

**If emergent:** Final alpha/G/h/Lambda differ significantly between runs
**If fundamental:** Final values converge to same equilibrium

### For Performance

- **COLD/WARM**: Can handle 10k-100k ticks
- **HOT**: Limit to 5k-10k ticks (explosive growth)
- **EXTREME**: Limit to 1k-5k ticks (may crash!)

### For Interesting Dynamics

**WARM START** is the sweet spot:
- Not too chaotic (like HOT)
- Not too boring (like COLD)
- Clear phase transition visible in data
- Completes in reasonable time

## Output Analysis

Each observer produces its own CSV with time-series data. To visualize:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load constants
df = pd.read_csv('results/constants_drift.csv')

# Plot alpha over time
plt.plot(df['tick'], df['alpha'])
plt.xlabel('Tick')
plt.ylabel('Alpha')
plt.title('Fine Structure Constant Evolution')
plt.show()
```

Compare early (high E) vs late (low E) phases to see energy effects.
