# Constants Drift Experiment Summary

## Experiment Configuration

**File:** `run_constants_experiment.py`
**Duration:** 4,040 ticks (40% of 10,000 target)
**Initial State:** 20 entities in small-world network (Watts-Strogatz topology)
**Update Rule:** CanonicalUpdateRule with Unseen-Age Energy Model

**Parameters (STABLE GROWTH preset):**
- `base_birth`: 0.05
- `base_expand`: 0.15
- `base_decay`: 0.15
- `base_rewire`: 0.10
- `base_bias`: 0.10
- `k_energy`: 0.50
- `k_cooling`: 0.01

## Constants Tracked

| Constant | Proxy Metric | Physical Analogy |
|----------|--------------|------------------|
| **alpha(t)** | Average clustering coefficient | Fine structure constant (coupling strength) |
| **G(t)** | Transitivity (global clustering) | Gravitational constant (clustering tendency) |
| **h(t)** | Minimum degree | Planck constant (quantum of action) |
| **Lambda(t)** | Entity growth rate | Cosmological constant (expansion rate) |

## Results

### Alpha (Fine Structure) - STABLE

**Range:** 0.786 - 0.995
**Mean:** 0.959
**Final:** 0.978

**Behavior:**
- Initial volatility (ticks 0-500): 0.79 - 1.0
- **Stabilizes around 0.96** after tick 500
- Small oscillations (±0.03) around equilibrium
- **Conclusion: Converges to stable value**

**Interpretation:**
The network quickly develops strong local clustering (most neighbors are also neighbors of each other) and maintains this structure. This is the graph equivalent of a "coupling constant" - it stays nearly constant once established.

---

### G (Gravitational) - MONOTONIC INCREASE

**Range:** 0.868 - 1.000
**Mean:** 0.989
**Final:** 1.000

**Behavior:**
- **Smooth monotonic increase** from 0.87 → 1.0
- Accelerates around tick 1,000
- Reaches perfect transitivity (G=1.0) by tick ~2,500
- **Stays at 1.0 thereafter**

**Interpretation:**
This is the most striking result. The network evolves toward **perfect triangle closure** - every pair of nodes with a common neighbor eventually becomes connected. This is the "gravitational" force - neighbors of neighbors attract. Once G=1.0, all possible triads have been closed into triangles.

**This is NOT drift - it's directional evolution toward maximum order.**

---

### h (Planck) - HIGHLY VOLATILE

**Range:** 0 - 74
**Mean:** 4.91
**Final:** 0

**Behavior:**
- **Extremely unstable**
- Spikes to 74 around tick ~800
- Multiple large oscillations (0 → 40 → 0)
- Collapses to **0 after tick 2,000**

**Interpretation:**
The "quantum of action" (minimum connectivity) is fundamentally unstable. Despite overall high network connectivity, the graph develops **isolated nodes** (degree = 0). This suggests:
- Some entities become completely disconnected
- Birth creates new isolated entities
- Decay can isolate previously connected entities
- No mechanism prevents degree from reaching zero

**This IS drift - wild, chaotic variance with no equilibrium.**

---

### Lambda (Cosmological) - DECAYS TO ZERO

**Range:** 0.000 - 0.037
**Mean:** 0.0006
**Final:** 0.000

**Behavior:**
- Spiky in early phase (ticks 0-500): frequent births
- **Exponential decay** toward zero
- Essentially zero after tick 2,000
- Only rare birth events thereafter

**Interpretation:**
The universe's expansion rate decays exponentially. Initial rapid growth (Lambda ~ 0.03 = 3% per tick) slows to **zero expansion** (Lambda = 0). The network reaches a **steady-state population**.

**This is NOT drift - it's exponential relaxation to equilibrium (zero).**

---

## Summary: Are Constants Stable?

| Constant | Behavior | Verdict |
|----------|----------|---------|
| **alpha** | Converges to 0.96 ± 0.03 | ✅ **STABLE** |
| **G** | Increases monotonically to 1.0 | ⚠️ **DIRECTIONAL** (not drift, but evolution) |
| **h** | Wild oscillations, no equilibrium | ❌ **UNSTABLE** (true drift) |
| **Lambda** | Decays exponentially to 0 | ✅ **STABLE** (at zero) |

**Conclusion:**
- **3 out of 4 constants stabilize** (alpha, G, Lambda)
- **1 constant drifts chaotically** (h - the "quantum")
- **Stable constants all tend toward MAXIMAL values** (alpha→1, G→1, Lambda→0)

This resembles a **"heat death" scenario**: Maximum local order (clustering), perfect triangle closure, zero expansion, but with quantum instabilities (isolated nodes).

---

## Energy Model Impact

### Current Behavior (Moderate Energy, E ≈ 0.5)

With `k_energy = 0.5` and immediate observation:
- `E0 = k_energy × T_unseen = 0.5 × 0 = 0` (still zero!)

**Same problem as genesis:** Immediate observation → no energy boost.

### Expected Behavior with Higher Energy

**Hypothesis:** Higher energy would **increase drift** in all constants.

**If E >> 1 (e.g., E0 = 100):**

| Constant | Predicted Effect |
|----------|------------------|
| **alpha** | Would **oscillate more** (rapid expansion/contraction disrupts clusters) |
| **G** | Would **decrease** (less time for triangles to stabilize before decay) |
| **h** | Might **stabilize higher** (more entities born = harder for all to isolate) |
| **Lambda** | Would **spike dramatically** then decay (birth_prob × 100 initially) |

**Mechanism:**
- High energy → massive birth rate → rapid expansion
- Network grows too fast for stable clustering
- Decay also increases but can't keep up
- Result: **Chaotic, non-equilibrium dynamics**

### To Test This

```python
# Simulate 1000 ticks before observation
update_rule = CanonicalUpdateRule(
    base_expand=0.15,
    base_decay=0.15,
    base_birth=0.05,
    base_bias=0.10,
    base_rewire=0.10,
    k_energy=5.0,      # High energy scaling
    k_cooling=0.001    # Very slow cooling
)

update_rule.set_unseen_age(1000)
# E0 = 5.0 × 1000 = 5000
# Cooling: tau = 0.001 × 1000 = 1
# Energy decays very quickly: E(t) = 5000 * exp(-t/1)
```

This would create:
- **Tick 0-1**: Explosive dynamics (E = 5000)
- **Tick 1-5**: Rapid cooling (E = 5000 → 37)
- **Tick 10+**: Near-equilibrium (E < 0.01)

**Constants would show:**
- **Early phase**: Wild oscillations in alpha, G, h, Lambda
- **Middle phase**: Rapid stabilization as energy decays
- **Late phase**: Similar to current results (stable constants)

---

## Relationship to Genesis

**Question:** Would higher energies in genesis affect constants?

**Answer:** **YES - fundamentally.**

The genesis experiment and constants experiment are **measuring the same substrate** with different observers:
- **Genesis observer** tracks: entities, edges, horizon, branching
- **Constants observer** tracks: alpha, G, h, Lambda

**They would show correlated effects:**

| Genesis Metric | Constants Analog | Energy Effect |
|----------------|------------------|---------------|
| Entity growth rate | Lambda | Both spike with high E |
| Edge growth rate | G | Both increase with high E initially |
| Avg degree | alpha | Both become unstable with high E |
| Horizon | (no direct analog) | Stays small if dense |

**High energy in genesis (E >> 1) would cause:**
1. **Lambda spikes** (matches explosive entity birth)
2. **alpha oscillates** (clusters form/break rapidly)
3. **G decreases initially** (network too dynamic for triangle closure)
4. **h fluctuates wildly** (nodes born/die/isolate rapidly)

**Then as energy decays (cooling):**
1. **Lambda → 0** (birth rate drops)
2. **alpha → 1** (clusters stabilize)
3. **G → 1** (triangle closure completes)
4. **h → 0** (some nodes end up isolated)

This would be **visible in the data**: all constants would show a **phase transition** from chaos (high E) to order (low E).

---

## Files Generated

- `results/constants_drift.csv` - Full time series (4,040 ticks)
- `results/constants_drift_log.txt` - Text log
- `results/constants_drift_analysis.png` - Visualization

## Conclusion

The constants drift experiment reveals:

✅ **Most "constants" are actually stable** (alpha, G, Lambda all converge)
⚠️ **One "constant" drifts chaotically** (h - minimum degree)
✅ **Stable constants evolve toward maximal order** (heat death scenario)

**Energy model insight:**
- **Low energy** (current): Constants stabilize quickly → boring equilibrium
- **High energy** (predicted): Constants would drift wildly → interesting dynamics

**To observe meaningful constant drift:**
1. Increase `k_energy` to 5-10
2. Simulate pre-observation period (`set_unseen_age(1000)`)
3. Run for 10k+ ticks to see full cooling curve
4. Compare early (hot) vs late (cold) constant values

This would demonstrate whether "physical constants" emerge from substrate dynamics (Tick-Frame hypothesis) or are truly fundamental.
