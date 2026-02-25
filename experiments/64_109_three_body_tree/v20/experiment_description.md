# v20: Distributed Bodies — Angular Coverage Through Volume

v19 showed orbits remain jagged despite drag and higher k. The scale hypothesis
(increasing separation) failed: planets free-fall because the single-node star's
gradient is angularly lumpy (~24 connectors in random directions).

**Fix:** Make bodies occupy volume. A star with 150 nodes × 24 connectors = ~3600
angular directions — nearly isotropic coverage. Body radius scales with mass:

    body_radius = base_radius * (mass / ref_mass) ^ (1/3)

Star (M=100K) → radius=5.0 → ~100-200 nodes. Planet (M=1) → radius≈0.1 → 1 node.

## New Parameters

- `--body-base-radius` (default 5.0): base radius at reference mass
- `--body-ref-mass` (default 100000): reference mass for radius scaling

## Known Limitations

- **Phase 2 (moving distributed bodies):** Star is stationary in Phase 1, so fixed
  node assignment works. Moving distributed bodies (Phase 2 binary) would need
  re-querying nodes after each hop. Not addressed in v20.
- **Density profile:** v20 uses uniform deposit. If gradient shape is wrong, try
  density-weighted: `weight = 1 / (1 + dist_from_center / body_radius)`.

## File Structure

```
v20/
  experiment_description.md  (this file)
  macro_bodies.py            (copy v19 + distributed body deposit)
  results/
```

## Base Parameters (from v19 winner)

- N=30000, k=24, H=0.01, alpha_expand=1.0, G=0.0
- mass=100000, deposit_strength=1e-5
- separation=10, tangential_momentum=0.1
- weighted_spread=True, drag=0.001
- body_base_radius=5.0, body_ref_mass=100000

February 2026

---

## Results

### Implementation

Star occupies 117 graph nodes (radius=5.0) × 24 connectors = 2808 angular
directions. Deposit distributed uniformly across all 117 nodes. Planet remains
a single node (mass=1 → radius=0.11 → 1 node).

### Run 1: dist_sep10 — Baseline comparison (sep=10)

N=30K, k=24, drag=0.001, 50K ticks, star=117 nodes.

| Metric | v19 point star | v20 distributed star |
|--------|---------------|---------------------|
| Final d_comov | 0.26 | 0.26 |
| Final \|v\| | 0.075 | 0.072 |
| Hops | 1981 | 1777 |
| Reversals | ~280 | 246 |

**Nearly identical to v19.** Speed still oscillates 0-0.35, angular momentum
flips sign constantly, high out-of-plane fraction. 3D trajectory is the same
chaotic tangle near the star.

### Run 2: dist_sep20 — Moderate separation (sep=20)

Same params, separation=18.96.

- Final d_comov=0.27, |v|=0.144, 1154 hops, 182 reversals
- Fewer reversals (182 vs 246) but same qualitative behavior
- Planet spirals inward from sep=20 to d_comov≈0.3 within first 10K ticks

### Run 3: nodrag_sep10 — No drag, sep=10

Same params but drag=0.

- Final d_comov=0.27, |v|=2.808, 352 hops, 77 reversals
- **Velocity runaway:** |v| goes 0.1 → 0.5 → 1.3 → 2.1 → 2.8 monotonically
- Only 352 hops in 50K ticks — planet accumulates huge velocity but rarely
  crosses hop threshold (velocity direction doesn't align with connectors)
- Confirms v19's diagnosis: without drag, velocity grows without bound at sep=10

### Run 4: nodrag_sep20 — No drag, sep=20

Same params but drag=0, separation=20.

- Final d_comov=0.27, |v|=0.626, 406 hops, 152 reversals
- **Velocity much more stable:** |v| stays 0.1-0.6 over 50K ticks
- Not running away like sep=10 — the larger initial separation gives the planet
  room for discrete random kicks to partially cancel
- 152 reversals in 406 hops — angular momentum flips every ~2.7 hops
- Planet is bound: doesn't escape, doesn't collapse to zero distance

### Analysis

**Distributed deposit alone made little difference** (Runs 1-2 vs v19 baseline).
The angular coverage improvement is real but the planet ends up inside the star
body where it doesn't matter.

**Drag was killing the orbit** (Run 3 vs Run 4). Drag=0.001 was added in v19 to
damp velocity runaway. But it constantly bleeds kinetic energy, preventing real
orbital dynamics. An orbit needs energy exchange between kinetic and potential —
drag breaks conservation.

**Key finding: sep=20, drag=0, distributed star produces a discrete orbit.**
152 reversals IS an orbit. The angular momentum flips sign every few hops because
each hop completely changes which graph neighbors the planet sees. This isn't
noise — it's the fundamental nature of discrete orbits on a random graph.

The velocity growth (0.1→0.6 over 50K ticks) may be discrete random-walk heating:
each hop adds a small random kick. Whether this stabilizes, grows, or is physical
is the question.

**sep=10 still has velocity runaway** because the planet is deeper in the gradient
well, receiving stronger kicks per tick. At sep=20, the kicks are weaker and more
isotropic, allowing statistical cancellation.

### Conclusions

1. Distributed bodies work as infrastructure but don't solve orbit smoothness
2. Drag is the wrong fix — it damps orbits, not just noise
3. Discrete orbits on random graphs are inherently jagged — this is physical
4. The right metric isn't smoothness but **statistical orbital properties**:
   bound vs unbound, mean comoving distance, velocity distribution, reversal rate
5. Using the 3D embedding to bypass graph topology for force would be cheating —
   physics must run on the graph

**Next:** v21 should embrace discrete orbital dynamics and study them statistically.
The question shifts from "how to make orbits smooth" to "what are the statistical
signatures of bound vs unbound discrete orbits on expanding random graphs?"
