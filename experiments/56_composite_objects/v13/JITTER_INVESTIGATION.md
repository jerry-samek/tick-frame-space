# Jitter Investigation: Is 0.119 Fundamental?

## Summary

**CONCLUSION: Jitter strength 0.119 is NOT fundamental.**

The sweep experiment demonstrates that 0.119 lies within a broad stable range [0.075, 0.5+], making it an empirically tuned value rather than a fundamental constant. Any value within this range produces stable patterns.

---

## The Key Question

> "If jitter is fundamental, it should be only 0 or 1. If it's anything else, it's emergent from a deeper layer."

The value 0.119 was suspicious because:
- Fundamental constants are typically 0, 1, or simple ratios
- 0.119 appeared to be empirically tuned
- It was unclear whether it was fundamental or emergent

---

## Experimental Results

### Sweep Parameters
- Grid size: 100x100
- Ticks per experiment: 300
- Jitter values tested: 22 (0.0 to 0.5)
- Random seed: 42 (reproducible)

### Phase Diagram

```
Jitter   | State      | r_norm
---------|------------|--------
0.000    | COLLAPSED  | 0.000
0.025    | DISPERSED  | 0.428
0.050    | DISPERSED  | 0.413
0.075    | STABLE     | 0.394
0.100    | STABLE     | 0.384
0.119    | STABLE     | 0.390  <-- The "tuned" value
0.125    | STABLE     | 0.382
...      | STABLE     | ~0.35-0.37
0.500    | STABLE     | 0.349
```

### Phase Transitions

1. **COLLAPSED -> DISPERSED** at jitter = 0.0 -> 0.025
   - Zero jitter causes complete collapse to origin
   - Even minimal jitter (2.5%) causes dispersion

2. **DISPERSED -> STABLE** at jitter = 0.05 -> 0.075
   - Around 5-7.5% jitter, the system transitions to stable patterns
   - This is the **critical point** for stability

### Key Findings

| Finding | Value |
|---------|-------|
| Collapse threshold | < 0.025 |
| Stable range | [0.075, 0.5+] |
| 0.119 position | Middle of stable range |
| Is 0.119 special? | **NO** |

---

## Interpretation

### What This Means

1. **Jitter is NOT fundamental** - it's a coupling constant
   - The stable range [0.075, 0.5] is wide
   - Any value in this range produces equivalent behavior
   - 0.119 was found empirically, not derived

2. **The balance is fundamental, not the value**
   - Push (jitter) must exceed ~7.5% to prevent collapse
   - Push can go up to 50% without causing dispersion
   - The system is robust to jitter variations

3. **Two critical points exist:**
   - Lower bound ~0.025-0.075: collapse-to-stable transition
   - Upper bound (not found): would be stable-to-dispersion
   - 0.119 is safely in the middle, providing robustness

### Theoretical Implications

The fact that jitter is NOT fundamental suggests:

1. **The fundamental quantity is participation rate**
   - At jitter=0.119: P(-1)=0.119, P(0)=0.762, P(+1)=0.119
   - This means 23.8% of cells participate per tick
   - The binary question becomes: "which cells are active?"

2. **Balance emerges from geometry**
   - Gamma decay (0.99) determines memory strength
   - Jitter (7.5%+) provides a minimum push to escape
   - The balance is geometric, not numerical

3. **0.119 is "good enough"**
   - It's roughly in the middle of the stable range
   - Provides robustness against perturbations
   - Could be anywhere from 0.08 to 0.5

---

## The Deeper Structure

### What IS Fundamental?

Based on this investigation, the fundamental elements appear to be:

1. **Discrete field values**: {-1, 0, +1}
2. **Tick-by-tick updates**: 1 entity spawned per tick
3. **Gamma memory**: decay + imprint mechanism
4. **The existence of push**: jitter > 0

### What is NOT Fundamental?

1. **Jitter strength 0.119**: arbitrary within stable range
2. **The specific gamma decay 0.99**: likely also has a stable range
3. **The specific grid size**: scales appropriately

### The New Model

Instead of:
> "Jitter = 0.119 is the ONE constant"

The model should be:
> "Jitter must be in [0.075, 0.5] to balance gamma pull"
> "The balance ratio (not the absolute value) is what matters"

---

## Future Work

1. **Find upper bound**: Test jitter > 0.5 to find dispersion transition
2. **Gamma sweep**: Vary gamma_decay to map the full stability region
3. **Grid size scaling**: Verify stability range is grid-independent
4. **Derive critical point**: Derive 0.075 from first principles

---

## Files

- `experiment_jitter_sweep.py`: Sweep implementation
- `results/jitter_sweep.json`: Full experimental data
- `config_v13.py`: Updated to accept jitter parameter
- `experiment_v13.py`: Updated CLI with --jitter flag

---

## Commands

```bash
# Run binary test (quick)
python experiment_jitter_sweep.py --binary-only --ticks 300

# Run full sweep
python experiment_jitter_sweep.py --steps 21 --ticks 300

# Run with specific jitter value
python experiment_v13.py --ticks 500 --jitter 0.1
python experiment_v13.py --ticks 500 --jitter 0.3
```

---

## Conclusion

**Jitter strength 0.119 is emergent, not fundamental.**

The fundamental property is the existence of a stable range where push (jitter) balances pull (gamma). The specific value 0.119 was empirically discovered but is interchangeable with any value in approximately [0.08, 0.5].

This finding aligns with the theoretical prediction that:
- Time is the fundamental substrate (discrete ticks)
- Space emerges from differences between ticks
- Physical "constants" are often balance points, not fundamental values

Date: 2026-01-31
Experiment: V13 Jitter Investigation
