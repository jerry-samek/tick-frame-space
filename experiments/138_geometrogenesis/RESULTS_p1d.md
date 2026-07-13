# Exp 138 P1d — RESULTS: dissipation channel + two-legged gate

**Date:** 2026-07-13. **Status:** CLOSED, skeptic-passed. **Prereg:** `PREREG_P1d.md` (frozen before the channel ran). **Supersedes** the dissipation-free recon `RESULTS_p1d_recon.md`.

## Question
Does adding the RAW 135 driven-dissipative "exhaust" loop (shed metabolism → dilute one hop 1/N(r) → reabsorb, Eddington cap → net deposit → starvation) to the directed-growth substrate drive it toward a finite low-dimensional manifold? (RAW 136 §5/§9: dissipation was the "missing ingredient" — Exp 138 P1 had drive + causality but no dissipation and only exploded/froze.)

## Outcome: **QUALIFIED (a)** — dissipation partially closes the wall
The blind `scalar_flux` dissipation loop drives the directed-growth substrate to a **finite-dimensional (ball-growth d≈2.2), degree-regularized (cv≈0.57 vs bare/growth-null 0.71–0.79), gate-MANIFOLD** graph on **large graphs (~2200–2800 nodes)**, **reproducibly across all surviving seeds**, in a **low-q critical band (q ≤ 0.30)**. Dissipation is **load-bearing** — bare growth never crosses cv=0.60 at any q; dissipation lowers cv by ~0.15 at matched q and is *required* to cross into the manifold regime. This is the RAW 135/136 "missing ingredient" doing what was predicted.

| q | #ext (of 6) | #manif (of survivors) | cv(diss) | ball-growth d | cv(bare) |
|---|---|---|---|---|---|
| 0.40 | 2 | 0 | 0.67–0.68 | 2.7 | 0.76 |
| **0.30** | 3 | **3/3** | **0.56–0.58** | **2.2** | 0.71 |
| 0.25 | 4 | 2/2 | 0.51–0.55 | 1.6 | 0.67 |
| 0.20 | 4 | 2/2 | 0.44–0.48 | — (too small) | 0.63 |

(`p1d_channel.py --plane`, c=1.5, scalar_flux, 6 seeds; gate `two_legged_gate.py`, frozen Qg_lo=0.13 D_lo=2.43 cv_hi=0.60.)

## The process error this closure records (the skeptic caught it)
The pre-registered `--fine` strength sweep **fixed q=0.40 — the single worst growth rate** — and on that basis I first concluded **outcome (b)** ("no manifold ever forms, dissipation erodes hubs but never regularizes"). That was **wrong**: it was an artifact of never lowering q. A fresh-context skeptic ran the (q,c) plane, found the q≤0.30 manifold window, and refuted (b). This is the fresh-context-skeptic pattern working exactly as intended — the operator's under-sweep was invisible from inside the operator's own framing. **Lesson (banked):** sweep the decision variable across its reachable range *before* freezing a conclusion; a negative from one slice of a plane is not a negative.

## The mechanism (a correction to the skeptic's "contra-A.8" framing)
The skeptic called this a "strong contra-A.8 positive." More precisely: **A.8 stands, and the manifold forms by a *different* route than A.5 proposed.** A.8 showed scalar flux is blind to *plaquette* structure — and indeed **Qg (the plaquette leg) stays low (~0.26)**, barely above threshold; the MANIFOLD verdict is **not** carried by plaquette reinforcement. It is carried by the **cv (degree-regularity) and D legs**: dissipation regularizes the degree distribution by **starving hubs** (a hub consumes over many edges but the diluted flux it reabsorbs cannot keep pace → it starves), collapsing the growth engine's preferential-attachment hubs (cv 0.79 → 0.57). So dissipation earns finite-d locality via **degree-regularization**, not via the A.5 plaquette-reinforcement route (which A.8 correctly killed). The `reconvergence` (topology-gated) arm adds nothing over blind `scalar_flux` — consistent both with A.8 (topology-gating of flux is irrelevant) and with the mechanism being degree-regularization rather than cycle-reinforcement.

## Three mandatory caveats (frozen prereg forbids tuning these away)
1. **It is a high-extinction CRITICAL BAND, not a broad basin.** 50–67% of seeds go extinct in the manifold window. Prereg (a)'s "low extinction" criterion is **not** met. This is a **self-organized-critical attractor** (narrow, dissipation-driven, high-mortality) — which is *exactly* the picture RAW 136 predicted (geometry as an SOC critical phase, not a knife-edge and not a broad basin). It vindicates the RAW 136 recipe (directed time + drive + dissipation → critical band) while denying any "robust basin" reading.
2. **d ≈ 2–3, NOT a pristine 2D lattice; the gate's D-leg OVERSTATES the low-dimensionality.** Out-of-gate ball-growth reads d≈2.2 (q=0.30) while the gate's lag-rank D reads ≈1.0. Report "finite-d, degree-regularized, cv≈0.57," **not** "a 2D manifold." Only the tiny q=0.20 graphs (≈140 nodes, mostly extinct) approach d≈2, and they are too small to bank.
3. **cv 0.51–0.58 clears the frozen cv_hi=0.60 by <0.05** → the MANIFOLD verdict is threshold-sensitive. But cv_hi was frozen pre-registration, so it **cannot** be moved to resurrect (b) — nor moved to make the positive look cleaner. Integrity cuts both ways.

## Net
Dissipation **partially closes** the geometrogenesis wall in this channel: finite-dimensional, degree-regularized locality is **earned from blind flux via hub-starvation**, in a high-extinction SOC critical band, on a substrate that without dissipation is a firmly crumpled hub (cv≥0.63, d≈4). It does **not** produce a pristine low-d manifold, and it does **not** leave the wall untouched (the recon's and my own first read). RAW 136 §7's "does a from-scratch DAG *produce* locality" is **partially answered YES** — locality (finite-d + degree-regularity) is produced, dimension is not pinned to 2/3 and the basin is critical not broad.

## Scope limits (honest, not tuned)
- One realization of the exhaust loop: **1-hop dilution**, this reabsorption rule, this Eddington cap. A different dilution/reabsorption could differ (the skeptic's multi-hop-dilution attack was not exhausted).
- `max_births` 3000; finite-size. The d≈2 corner needs larger graphs to bank.
- The gate D-leg / ball-growth **disagreement** (D≈1 vs d≈2.2) is an unresolved instrument issue — the D-leg understates dimension on these graphs; a future gate should reconcile lag-rank with ball-growth.
- The manifold verdict rests on the **cv leg** with a <0.05 margin; the plaquette (Qg) leg is near-floor. A stricter instrument might reclassify.

## Banked next (fresh prereg required)
Fully map the (q,c) plane and the extinction boundary; larger `max_births` to test whether d→2 is reachable off the extinction edge; reconcile the D-leg/ball-growth dimension disagreement; test multi-hop dilution (the one skeptic attack not run to ground); characterize the SOC band (avalanche/mortality statistics) to test the RAW 136 SOC claim directly.

## Provenance
Prereg frozen `1c21e61`; channel `159611c`; gate hardened `7002e78`; wiring + sweeps `<this commit>`. Two fresh-context skeptic passes (one on the gate/probe recon → A.8; one on this channel result → refuted the operator's (b), established qualified (a)).
