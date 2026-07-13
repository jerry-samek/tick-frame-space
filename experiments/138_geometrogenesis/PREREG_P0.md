# Exp 138 Phase P0 — Trugenberger condensation positive control — PRE-REGISTRATION

**Date frozen:** 2026-07-10, after G-I0 PASS (`results/i0.json`), before `p0_condensation.py` exists.
**Role (spec §4):** positive control. Proves (a) a geometric phase is reachable inside graph dynamics, (b) our I0c instrument detects it. Sign-level replication of cycle condensation (arXiv:1610.05934, 1811.12905) under OUR declared action — not numeric replication of published curves.

## Deviation from the implementation plan, made BEFORE this freeze (logged)

The plan declared a Jost-Liu action. Discovered while designing this PREREG: under the hard-core (triangle-free) condition of the Kelly-Trugenberger setup, every edge has t = 0 common neighbors, making κ_JL a degree-only constant — **blind to the square condensation that drives the transition**. The action therefore uses **exact Ollivier curvature**, computable exactly and cheaply for k-regular graphs: both neighbor measures are uniform on k points, so W₁ = (1/k)·min-cost perfect matching (Birkhoff — extreme points of the equal-uniform-marginal transportation polytope are permutation matrices), enumerable over k! = 24 permutations at k=4. The fast path `kappa_exact_regular` must be validated against the LP `kappa_exact` on random graphs before production (unit test).

## Model (frozen)

- N = 256, k = 4 random regular graph, initial condition repaired to triangle-free (seeded swaps until no triangles).
- **Hard-core constraint:** moves creating a triangle are rejected (Kelly-Trugenberger condition).
- **Action:** H = −J · Σ_edges κ_exact(i, j) (uniform neighbor measures, no laziness, graph-distance cost with BFS cutoff 3).
- **Move:** double-edge swap (a,b),(c,d) → (a,c),(b,d); rejected on self-loop, multi-edge, or triangle creation. ΔH computed over edges with an endpoint within distance 1 of {a,b,c,d} (radius-1 ball; κ reaches distance-2 structure, so this is still an approximation — DECLARED — with residual drift monitored by full-energy recomputation and resync every 25 sweeps, drift reported per checkpoint). *Pre-run amendment (2026-07-10, before any ladder run):* the plan's incident-edges-only ΔH showed drift ±50 per 100 sweeps in the N=128 smoke; widened to the radius-1 ball and resync tightened 100→25. Consequence for interpretation, stated up front: sampling is approximate-Boltzmann between resyncs; the gate claims condensation-and-detection (sign-level), not exact equilibrium sampling.
- **Metropolis:** β = 1, accept iff ΔH ≤ 0 or rng() < exp(−ΔH).
- **Ladder:** J ∈ {0.5, 1, 2, 4, 8}; 1500 sweeps (1 sweep = N attempted moves); 10 seeds per J; multiprocessing across (J, seed).
- **Checkpoints (every 100 sweeps):** energy, acceptance rate, I0c classification of the current graph, mean κ, square count per edge (squares counted exactly on the ≤2-neighborhood of each edge).

## Gate G-P0 (frozen)

- ∃ J in the ladder with ≥ 8/10 seeds ending classified `poly` (I0c), AND at the smallest J ≥ 8/10 seeds remain `exp` — the transition visible, signed both ways.
- Escape hatch (once): if no J condenses, extend to J ∈ {16, 32} at 5000 sweeps, 10 seeds. Beyond that P0 FAILS; program stops for diagnosis (instrument vs replication, via I0 controls at N=256).
- Reported, not gated: ê of condensed graphs vs band_2d (bands were calibrated at larger N; classification transfers, exponent values are approximate at N=256 — near-boundary readings flagged per `control_margin` = 0.0258).
