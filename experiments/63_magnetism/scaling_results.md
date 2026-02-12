# Scaling Experiment — Analysis

**Date**: February 12, 2026

## Question

Does the transport anisotropy signal survive at larger grids and higher entity density, or is it lattice
contamination?

## Configurations Tested

| Config      | Grid    | Entities | Spacing | Purpose           |
|-------------|---------|----------|---------|-------------------|
| 64x64_4x4   | 64x64   | 4x4 (16) | 16      | Baseline          |
| 128x128_4x4 | 128x128 | 4x4 (16) | 32      | 2x resolution     |
| 256x256_4x4 | 256x256 | 4x4 (16) | 64      | 4x resolution     |
| 64x64_8x8   | 64x64   | 8x8 (64) | 8       | 4x entity density |

All runs: signed mode, eq=1000 ticks, probe=2000 ticks, 3 runs/pattern.

---

## Finding 1: M_net discrimination is scale-independent (REAL PHYSICS)

| Config      | Checkerboard | Stripe  | Ferromagnetic | Antiferromagnetic |
|-------------|--------------|---------|---------------|-------------------|
| 64x64_4x4   | 2.2e-13      | 1.8e-12 | **80,000**    | 4.6e-13           |
| 128x128_4x4 | 3.5e-13      | 2.6e-12 | **80,000**    | 1.5e-12           |
| 256x256_4x4 | 1.1e-12      | 6.6e-13 | **80,000**    | 3.6e-12           |
| 64x64_8x8   | 3.8e-13      | 1.3e-12 | **320,000**   | 2.7e-13           |

Compensated magnetism is **perfectly robust** at all scales. Compensated patterns give M_net at machine
epsilon (~1e-13) regardless of grid size or entity count. Ferromagnetic gives M_net = n_entities * omega *
W_tang * eq_ticks exactly. This is a conservation law (`sum(tang) = sum(all deposits) = W_tang * sum(all omegas)

* ticks`), not a lattice artifact.

The 8x8 ferromagnetic gives 320,000 = 64 * 1 * 5 * 1000, exactly 4x the 4x4 value. Perfect.

**Verdict: The magnetic topology (which patterns are compensated vs uncompensated) is real physics.**

---

## Finding 2: Transport anisotropy SNR does NOT converge (NOISY)

| Config      | Checker SNR | Stripe SNR |
|-------------|-------------|------------|
| 64x64_4x4   | 0.87        | 1.63       |
| 128x128_4x4 | 3.69        | 6.24       |
| 256x256_4x4 | 2.08        | 1.91       |
| 64x64_8x8   | 2.26        | 1.33       |

SNR = |mean deflection| / std(deflection) across 3 runs.

The SNR jumps from 64 to 128 but then **drops back** at 256. It does not monotonically improve with
resolution. The 8x8 density test gives intermediate values. With only 3 runs, these estimates are
themselves noisy (chi-squared with 2 dof gives ~50% uncertainty on std).

However, the deflection magnitudes are consistently in the 0.7-2.1 range across all configurations —
the signal doesn't vanish at larger grids. It's just that the **variance across random initial thetas
dominates** the inter-run variation, making it hard to extract a clean angular preference.

**Verdict: Transport anisotropy is real but dominated by initial-condition sensitivity. It doesn't
clean up with resolution alone. The signal is there (non-zero deflections at all scales) but its
direction is set by the random initial thetas, not the pattern geometry.**

---

## Finding 3: Fourier modes reveal lattice contamination

### Stripe pattern — m=4 is physical but competes with lattice m=8

| Config      | m=4       | m=8       | Dominant |
|-------------|-----------|-----------|----------|
| 64x64_4x4   | **0.512** | 0.445     | **m=4**  |
| 128x128_4x4 | **0.507** | 0.472     | **m=4**  |
| 256x256_4x4 | 0.311     | **0.589** | m=8      |
| 64x64_8x8   | **0.487** | 0.478     | **m=4**  |

At 64 and 128, stripe's 2x2 block structure produces a physical m=4 signal that narrowly dominates the
lattice m=8 mode. But at 256x256, the halos are too spread out relative to spacing, the overlap
diminishes, and the lattice signature (m=8) takes over.

The 8x8 density test maintains m=4 dominance because closer entities produce more halo overlap,
reinforcing the block structure. This confirms that m=4 IS the physical signal from the 2x2 pattern,
and it requires sufficient entity-entity interaction (halo overlap) to dominate the lattice.

### Checkerboard pattern — no clean d-wave signal

| Config      | m=2   | m=4   | m=8       | Dominant |
|-------------|-------|-------|-----------|----------|
| 64x64_4x4   | 0.070 | 0.222 | **0.482** | m=8      |
| 128x128_4x4 | 0.074 | 0.328 | **0.380** | m=8      |
| 256x256_4x4 | 0.121 | 0.178 | **0.426** | m=8      |
| 64x64_8x8   | 0.147 | 0.038 | **0.493** | m=8      |

Checkerboard never achieves m=2 or m=4 dominance at any scale. The expected d-wave (m=2) signal is
always weak (0.07-0.15). The m=4 component peaks at 128x128 (0.328) but never exceeds m=8. At 8x8
density, m=4 drops to 0.038 while m=2 rises to 0.147 — the angular structure changes character
depending on entity count, which is a lattice sensitivity signal.

### Antiferromagnetic — m=8 dominant everywhere, as expected

The row-alternating pattern produces no angular structure beyond the lattice mode. m=8 dominates (0.34-0.77)
at all scales. At 256x256, some m=6 (0.328) appears, likely from the interaction of row structure with
lattice geometry.

**Verdict: The 8-direction rotation creates an intrinsic m=8 lattice contamination. Physical angular
modes (stripe m=4) can emerge but only when entity halos overlap sufficiently. Checkerboard's expected
d-wave is too weak to compete with the lattice.**

---

## Finding 4: Off-diagonal conductivity does not converge

| Config      | Checker sigma_xy | Stripe sigma_xy |
|-------------|------------------|-----------------|
| 64x64_4x4   | +0.044           | -0.038          |
| 128x128_4x4 | +0.030           | -0.105          |
| 256x256_4x4 | +0.205           | -0.068          |
| 64x64_8x8   | -0.209           | +0.010          |

Sign flips between configurations. No convergence. The off-diagonal conductivity is dominated by the
specific geometry of probe positions relative to the entity grid, not by the magnetic pattern.

**Verdict: Lattice noise. The sigma_xy signal is not a robust physical observable at these scales.**

---

## Summary

| Observable                        | Scale-independent?            | Physical?                         |
|-----------------------------------|-------------------------------|-----------------------------------|
| M_net (compensated magnetism)     | Yes, exact at all scales      | **Real** (conservation law)       |
| Deflection magnitude (            | defl                          | )                                 | Consistent ~1-2 rad | **Real** but noisy |
| Deflection direction (A_NS, A_EW) | No, varies with initial theta | **Lattice-sensitive**             |
| Fourier m=4 (stripe)              | Yes at small/medium spacing   | **Physical** (needs halo overlap) |
| Fourier m=2 (checker d-wave)      | No, never dominant            | **Too weak** to extract           |
| Off-diagonal sigma_xy             | No, sign flips                | **Lattice noise**                 |

## Implications

1. **The signed tangential field correctly captures magnetic topology.** The ferro/compensated
   discrimination is exact physics, scale-independent, and emerges purely from the conservation of
   signed deposits. This validates the approach.

2. **Transport anisotropy needs more than 8-direction rotation.** The 8-fold lattice symmetry overwhelms
   the physical angular signal. To extract clean d-wave or g-wave transport, the simulation would need:
    - Finer angular resolution (16 or 32 directions instead of 8)
    - Much denser entity grids (so halos overlap and form a continuous medium)
    - Or a fundamentally different probe coupling mechanism

3. **The 8x8 density direction is more promising than resolution scaling.** Doubling the grid with same
   entity count (256x256_4x4) makes things worse — the entities are too isolated. Increasing density
   (64x64_8x8) at least maintains the stripe m=4 signal and produces comparable deflection magnitudes
   with 4x fewer cells to compute.
