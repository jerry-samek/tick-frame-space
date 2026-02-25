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
