# Experiment 131 — Closure

**Status:** Closed. April 19, 2026.
**Outcome:** Lineage tree + local conductance flow does NOT recover Newton's
1/r in 3D. Three independent flow rules tested, three independent failure
modes, converging on the same diagnosis: the lineage tree's connectivity
is fundamentally not a 3D Laplace topology, and no choice of per-edge
conductance can fix it.
**Supersedes:** —
**Succeeded by:** Experiment 132 (Anisotropic Connectors on RGG).

---

## Trajectory Summary (v1 → v7)

Experiment 131 tested the hypothesis from RAW 131: connections are
ancestral, not spatial; +1/tick flows through always-present lineage
edges; Newton emerges from tree self-similarity + 3D embedding.

### v1–v4 (April 18): naive averaging diffusion

`ρ_new[i] = mean(ρ[neighbors])`. Tested across multiple boundary
fractions (0.50, 0.70, 0.90), branching k=8, depth D=5.

| Config | bf | slope ρ | regime |
|--------|-----|---------|--------|
| v2 | 0.70 | −0.99 | middle, looked like Newton |
| v3 | 0.50 | −2.01 | compressed cliff |
| v4 | 0.90 | −0.17 | saturated pool |

v2's slope ≈ −1 looked like Newton recovery initially. Phase 2 (tangential
Schwarzschild transfer) showed ρ(r) is not a clean power law — fit slope
depends heavily on window. v3/v4 confirmed the v2 result was a lucky
middle between two failure modes, not a physical law.

**Falsified:** naive averaging on the tree.

### v5 (April 19): conductance-weighted flow, c = 1/ℓ (resistor analogue)

Per-edge conductance c_ij = 1/length(edge). Flow becomes weighted
average. 3 seeds × 3 boundaries on D=5 tree.

| bf | mean slope ρ | std |
|----|--------------|-----|
| 0.50 | −1.66 | 0.22 |
| 0.70 | −1.40 | 0.33 |
| 0.90 | −1.20 | 0.15 |

Pathological regime swing eliminated; slopes monotone in bf, in [−2, −1].
bf=0.9 mean −1.20 ± 0.15 sat at the edge of [−1.2, −0.8] success band.
Not a confirmation, not a falsification — limited dynamic range
(fit window only ~0.7 decade on R_max ≈ 8.6).

### v6 (April 19): same flow, deeper tree (D=6)

8× more nodes (~300k), R_max grows asymptotically toward
`R_ROOT × SCALE/(SCALE−1) = 10`. D=6 reached 9.3.

| bf | mean slope ρ | resid (log units) |
|----|--------------|-------------------|
| 0.50 | −3.08 | 0.76–1.05 |
| 0.70 | −3.16 | 0.86–1.31 |
| 0.90 | −3.00 | 0.89–1.45 |

Boundary stability much improved (slopes essentially flat across bf).
**But the slope itself moved away from −1, into −3 territory, with
huge residuals (ρ varies by ~3× from any 1/r line).**

Diagnosis: conductance c=2^d/R_ROOT spans 32× between depth-1 (c=0.2)
and depth-6 (c=6.4) edges. Short inner-tree edges dominate flow; field
decays rapidly with tree-depth, not spatial distance. Adding depth
amplified the asymmetry.

### v7 (April 19): conductance-form sweep

Three forms on the same D=5 tree, single seed × 3 boundaries.

| form | bf=0.50 | bf=0.70 | bf=0.90 | spread |
|------|---------|---------|---------|--------|
| **uniform** (c=1) | −1.09 | −0.50 | −0.17 | 0.92 |
| **inv_length** (c=1/ℓ) | −1.39 | −1.08 | −1.05 | 0.34 |
| **length** (c=ℓ) | −0.76 | −0.29 | −0.07 | 0.69 |

Three distinct failure modes:
- **c=1**: cliff-vs-saturation transition with bf (v3/v4 reproduction).
- **c=1/ℓ**: short-edge-dominated, slope drifts toward −1 only at one bf.
- **c=ℓ**: long-edge highways; field equilibrates uniformly within 6k
  ticks (bf=0.9 mean=0.913, then zero delta forever); slope flattens.

Whichever edge-length regime dominates determines the answer, and 3D
Newton is not the answer for any of them.

---

## Load-Bearing Result

**The lineage tree's topology is the bottleneck, not the flow rule.**
Across the natural conductance space {c=1, c=1/ℓ, c=ℓ}, every form
fails differently and none produces a robust 1/r profile. Local-flow
rules cannot transform tree connectivity into 3D Laplace topology.

---

## What Survives From RAW 131

RAW 131's specific claim — *tree + local flow → Newton* — is falsified.
Its broader ontological claims have not been tested by Exp 131 and
remain live for revisit in a different operational framing:

- Connections as ancestral structural facts (not built by propagation).
- `c` emerging from LCA-traversal time on a self-similar tree.
- Cosmological horizon as LCA-depth-limited.
- Pattern coherence as a property of subtree intactness.

None of these required the local-flow-gives-Newton bridge. They could
be operationalized differently — e.g. as constraints on which
substrates are admissible, rather than as the substrate itself.

---

## Diagnosis (the handoff to Experiment 132)

Two readings of the v5–v7 negative remain on the table:

### (a) The lineage tree is the wrong substrate entirely

The RGG (Exp 128 v11) actually got us 1/r², Kepler, and exact
tangential Schwarzschild. Its only failure was radial Schwarzschild,
diagnosed (Phase 6/6b/6c/6d/6e) as missing connector anisotropy near
mass. Experiment 132 takes this reading: keep the RGG, add the missing
ingredient (anisotropic connector reshaping), and see if Schwarzschild
radial earns through.

### (b) The lineage tree needs non-local rules

Conductance flow is local. Maybe the right operations on a lineage
tree are non-local — e.g. propagation that respects LCA depth, or
flow that reads subtree size. We have not tested this. It is a
theoretically larger space and harder to motivate without further
insight from RAW 131.

(a) is concrete and motivated by Exp 128's specific diagnosis. We take
(a). (b) remains a parking lot for if (a) also fails.

---

## What This Experiment Costs in Assumptions

- The v2 result (slope ≈ −1, hand-confirmed Newton recovery) is
  retracted. It was a fit-window artifact.
- RAW 131's prediction "Phase 5's tangential Schwarzschild transfers
  trivially" was never reached because Phase 1 never produced a clean
  ρ(r). That prediction is therefore neither confirmed nor refuted.
- The "ancestral connections" ontology is not falsified, but it has
  not earned anything operational either. It remains philosophically
  appealing; experimentally inert.

---

## Files and Pointers

- `experiment_description.md` — original April 18 spec.
- `phase1_newton_from_tree.py` — v1/v2 (naive averaging, gaussian).
- `phase1v3_newton_from_tree.py` — v3/v4 (uniform offsets, spatial star).
- `phase2_tangential_schwarzschild.py` — Phase 2 (failed transfer).
- `phase1v5_conductance.py` — v5 (c = 1/ℓ, D=5, 3 seeds × 3 bf).
- `phase1v6_deeper.py` — v6 (c = 1/ℓ, D=6).
- `phase1v7_cond_sweep.py` — v7 (3-form sweep, D=5, single seed).
- `results/` — logs and plots for all phases.
- `docs/theory/raw/131_lineage_substrate.md` — RAW 131.

---

## One-Line Closure

Experiment 131 ruled out lineage tree + local conductance flow as a
substrate that recovers Newton in 3D. The RGG remains the best-known
substrate for the geometric content of GR; its open frontier (radial
Schwarzschild) is the explicit handoff to Experiment 132 (anisotropic
connectors on RGG).
