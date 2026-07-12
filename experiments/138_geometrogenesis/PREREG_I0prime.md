# Exp 138 Phase P1d I0' — null-safe dimension instrument — PRE-REGISTRATION

**Date:** 2026-07-12. **Motivation:** P1c (see `RESULTS_p1c.md` / `PREREG_P1C.md`) found that the spectral
dimension estimator `ds_sparse` alone is fooled by a random 4-regular graph, which reads `d_s ≈ 2.0` — a
false manifold. Exp 138 P1d needs a dimension instrument that survives this null before it can be used to
gate anything about annealing/geometrogenesis. This document freezes that instrument (I0') before any code
is written, per TDD discipline.

## Background: what already exists and what is reused

- `instrument.fit_exponent` / `instrument.shell_counts` (Exp 138 Phase I0c, frozen in `PREREG_I0c.md`):
  classifies a graph's ball-growth as `poly` (lattice-like) or `exp` (expander/tree-like) from BFS shell
  counts. Already validated 10/10 against `random_regular` reading `exp` (see `results_i0_console.txt`).
  This classifier is **not** by itself sufficient for P1d, because P1d's dynamics can produce graphs that
  are not literal random-regular graphs but could still degenerate in ways the shell classifier alone might
  miss — hence the second, independent feature below.
- `p1c_recon.ds_sparse`: spectral dimension via lazy-walk return probability. This is the estimator that
  P1c showed reads `d_s ≈ 2.0` on a random 4-regular graph (the false-manifold failure). It is retained in
  I0' as a **reported** diagnostic value only — it never gates `is_manifold`.
- `graphs.{torus2d, torus3d, binary_tree, random_regular}` (Exp 137): signed control graph constructors.

## Estimator I0' (frozen)

A graph reads **`is_manifold = True`** iff **both**:

1. `shell_cls == "poly"` (the existing I0c ball-growth classifier), **AND**
2. `cyc_density ≥ cyc_thresh`, where `cyc_density` = mean number of undirected 4-cycles through a node
   (short-cycle density; see `short_cycle_density` below).

`d_spectral` (`ds_sparse`) and `d_shell` (`fit_exponent`'s `e_hat`) are both **reported** as the dimension
value estimates, with their own known biases (lattice-calibrated), but **do not gate** `is_manifold`.

### Rationale for the two-part rule and why it is P1c-proof

The P1c failure mode was gating on spectral `d_s` alone: a random 4-regular graph has no manifold structure
at all, yet its return-probability decay slope reads `d_s ≈ 2.0`, indistinguishable from a genuine 2D
lattice under that single estimator. Two independent structural facts about random-regular graphs are true
regardless of that spectral coincidence:

- They are **locally tree-like** (girth grows with N; short cycles are asymptotically rare) — so
  `cyc_density → 0` as N grows, while a 2D/3D lattice has `cyc_density` of order 1 per node (a square
  lattice has essentially exactly one 4-cycle per node in the bulk).
- The existing I0c shell classifier already reads random-regular graphs as `exp`, not `poly` (validated
  10/10 in `results_i0_console.txt`).

Requiring **both** `shell_cls == poly` and high `cyc_density` means a graph must fool *two independently
motivated* structural readings simultaneously to be misclassified as a manifold — the random-regular null
fails hard on both axes at once (tree-like shell growth AND near-zero short-cycle density), which is why
this rule is expected to be robust where the single-feature (`d_s` alone) rule was not.

### `short_cycle_density`

Mean count of undirected 4-cycles through a node, i.e. for a node `v` with neighbours `nb`, count pairs
`(nb[i], nb[j])` that share a common neighbour other than `v`, summed over all nodes and normalized by
`2 * n` (each 4-cycle is counted twice — once from each of its two "opposite" corners' neighbour-pair
intersections). This is a purely local, deterministic, seed-independent computation (no rng involved).

## Signed controls (the null is mandatory)

- `torus2d(24)` → `is_manifold = True`
- `torus3d(12)` → `is_manifold = True`
- `binary_tree(10)` → `is_manifold = False` (fails on `shell_cls == exp`)
- `random_regular(N, 4)`, 10 seeds → `is_manifold = False` — **the P1c null.** Must fail on *both*
  `shell_cls` and `cyc_density`, not just one.
- `random_regular(N, 6)`, 10 seeds → `is_manifold = False` — same null, second degree, to check the rule
  is not an artifact of degree 4 specifically.

## Gate G-I0' (frozen)

- All lattice controls (`torus2d`, `torus3d`) read `is_manifold = True`.
- `binary_tree` reads `is_manifold = False`.
- **Both** `random_regular(N,4)` and `random_regular(N,6)` read `is_manifold = False` on **≥ 9/10 seeds**
  each.
- On PASS: freeze `cyc_thresh` = the halfway point (geometric mean) between the minimum lattice
  `cyc_density` observed across controls and the maximum random-regular `cyc_density` observed across all
  20 random seeds (both degrees pooled for the max). Record `control_margin` = that gap
  (`min_lattice_cyc_density - max_random_cyc_density`, i.e. how far apart the two populations sit) into
  `results/i0prime.json`.
- **FAIL any of the above** → the two-part rule is insufficient. Per this pre-registration, the fallback is
  to redesign under a **fresh PREREG** adding a **candidate third discriminating feature**, named in advance
  as: **spectral-gap** and/or **`d_shell`-vs-`d_spectral` agreement** (i.e. the two independently-derived
  dimension estimates disagreeing signals non-manifold structure even when each alone might pass). The null
  is non-negotiable — under no circumstance is `cyc_thresh` (or the shell classifier) to be weakened or
  retuned specifically to force a control to pass.

## Interface (frozen)

```
dimension_instrument.short_cycle_density(adj) -> float
dimension_instrument.classify_dimension(adj, rng, n_sources=64) -> dict
    {"shell_cls": "poly"|"exp"|"degenerate", "d_shell": float, "d_spectral": float,
     "cyc_density": float, "is_manifold": bool}
```

`is_manifold` is the P1d gate observable used by all downstream tasks in this phase.

## Determinism

All stochastic choices (source sampling for `shell_counts`/`ds_sparse`, random-regular graph construction)
go through a caller-supplied seeded `numpy.random.default_rng`. `short_cycle_density` itself is fully
deterministic (no sampling) and iterates node/neighbour sets via `sorted(...)` to avoid any set/dict
iteration-order dependence.
