# Genesis Experiment Summary

## Experiment Configuration

**File:** `run_genesis_experiment.py`
**Duration:** 3,700 ticks (stopped early, target was 100,000)
**Initial State:** 3 entities in triangle topology
**Update Rule:** CanonicalUpdateRule with Unseen-Age Energy Model

**Parameters (SPARSE GROWTH preset):**
- `base_birth`: 0.10
- `base_expand`: 0.20
- `base_decay`: 0.25
- `base_rewire`: 0.15
- `base_bias`: 0.10
- `k_energy`: 0.01 (default)
- `k_cooling`: 0.005 (default)

## Results

### Growth Metrics

| Metric | Initial | Final | Growth Factor |
|--------|---------|-------|---------------|
| **Entities** | 11 | 372 | 33.8× |
| **Edges** | 1 | 61,420 | 61,420× |
| **Avg Degree** | 0.18 | 330.22 | 1,835× |
| **Network Density** | ~1% | ~89% | Nearly complete graph |

### Key Observations

1. **Explosive Edge Growth**
   - Edge count grows **1,835× faster** than entity count
   - Network becomes nearly complete (89% of all possible edges exist)
   - Final state: almost every entity connected to almost every other entity

2. **Horizon Collapse**
   - Stays at 1-2 throughout the experiment
   - Everything is maximally connected (1-2 hops away)
   - Characteristic of dense, small-world networks

3. **Performance Degradation**
   - Simulation slows dramatically as graph densifies
   - From ~3,300 ticks/sec → ~600 ticks/sec by tick 2,200
   - Processing 61k edges per tick becomes expensive

4. **Low Energy Regime**
   - Observer attached at tick 1 → `T_unseen ≈ 0` → `E0 ≈ 0`
   - All probabilities operate near their base values
   - Decay is slightly boosted: `decay_prob = base × (1 + 1/(1+E)) ≈ 2×base`
   - Birth/expand operate at base rates
   - Result: **triangle closure and preferential attachment dominate**

## Energy Model Impact

### Current Behavior (Low Energy, E ≈ 0)

The Unseen-Age Energy Model with immediate observation produces:
- **Dense local clusters** (triangle closure very active)
- **Preferential attachment** (high-degree nodes attract more connections)
- **Slow birth rate** (only ~0.10 per tick)
- **Moderate decay** (0.25, but not enough to prevent runaway edge growth)

### Expected Behavior with Higher Energy

**If `k_energy = 5.0` (50× increase):**

With `T_unseen = 0` but higher scaling:
- `E0 = k_energy × T_unseen = 5.0 × 0 = 0` (still zero!)

**Key Insight:** Higher `k_energy` alone doesn't help if observer attaches immediately!

**To get high energy, you need EITHER:**

1. **Delayed observation:**
   ```python
   update_rule.set_unseen_age(1000)  # Simulate 1000 ticks before observation
   # Then: E0 = k_energy × 1000 = 10 (with default k_energy=0.01)
   ```

2. **Much higher k_energy + some unseen time:**
   ```python
   k_energy = 10.0
   # Even 10 unseen ticks → E0 = 10.0 × 10 = 100
   ```

### Predicted Effects of High Energy (E >> 1)

| Probability | Formula | Low E (≈0) | High E (≈100) |
|-------------|---------|------------|---------------|
| **Expand** | `base × (1 + E)` | 0.20 | ~20.0 |
| **Decay** | `base × (1 + 1/(1+E))` | ~0.50 | ~0.25 |
| **Birth** | `base × (1 + E)` | 0.10 | ~10.0 |
| **Bias** | `base × (1 + E)` | 0.10 | ~10.0 |

**Result:** Explosive expansion, massive birth rate, but edges decay faster to compensate.

**Would this affect constants?** **YES, dramatically:**
- **alpha**: Would fluctuate wildly as rapid expansion/contraction occurs
- **G**: Would decrease (less time for triangles to form before decay)
- **h**: Would likely stay higher (more entities born = harder for all to reach degree 0)
- **Lambda**: Would spike massively (birth rate = 10.0 per tick!)

## Recommendations

### For Denser Growth with Control

Use **higher base values** instead of relying on energy model:
```python
balanced = dict(
    base_expand=0.3,
    base_decay=0.1,   # Lower decay
    base_birth=0.2,   # Higher birth
    base_bias=0.15,
    base_rewire=0.1,
    k_energy=0.01,    # Keep energy model minimal
    k_cooling=0.005
)
```

### For Energy-Driven Dynamics

Simulate pre-observation universe:
```python
update_rule = CanonicalUpdateRule(
    base_expand=0.1,
    base_decay=0.1,
    base_birth=0.05,
    base_bias=0.05,
    base_rewire=0.05,
    k_energy=1.0,     # High energy scaling
    k_cooling=0.01    # Slow cooling
)

# Simulate 5000 ticks of unseen evolution
update_rule.set_unseen_age(5000)
# Then attach observers → E0 = 50, decays slowly
```

This creates a "hot early universe" that cools down after observation begins.

## Files Generated

- `results/genesis_metrics.csv` - Full time series
- `results/genesis_log.txt` - Text log
- `results/genesis_sparse_growth.png` - Visualization (from 200-tick run)

## Conclusion

The genesis experiment successfully demonstrates:
- ✅ Entity birth and graph growth from minimal seed
- ✅ Network densification through preferential attachment
- ✅ Horizon collapse in dense networks

However, with **low energy** (immediate observation):
- ❌ Growth becomes **too explosive** (edges >> entities)
- ❌ Network becomes **nearly complete** (loses interesting structure)
- ❌ Performance degrades significantly

**Next steps:**
1. Test with higher `k_energy` + delayed observation
2. Or use simpler base parameters without energy model
3. Consider adding entity **death** probability to balance birth
