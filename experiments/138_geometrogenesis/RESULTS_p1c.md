# Exp 138 Phase P1c — RESULTS: engagement-vs-connectivity tradeoff of directed selection

**Dates:** 2026-07-11 (recon, PREREG freeze, sweep, skeptic pass, disqualification tests, this doc).
**Pre-registration:** `PREREG_P1C.md` (frozen after `p1c_recon.py`, before the sweep).
**Code/data:** `p1c_recon.py`, `p1c_run.py`, `p1c_recon.py::ds_sparse`; `results_p1c_recon_console.txt`, `results_p1c_console.txt`, `results_p1c_skeptic_console.txt`; `results/p1c.json`.

## Verdict

**TRADEOFF-CONFIRMED** — directed cycle-closure selection under quench cannot produce a connected + engaged + geometric state; connectivity and engagement are anticorrelated (Spearman −0.54 across cells), and the lone letter-passing cell is a disqualified instrument artifact. **Plus a load-bearing instrument finding:** the spectral-dimension gate was never valid at this scale — a random 4-regular graph reads d_s ≈ 2.0, inside the "2D band."

Path to this verdict (all corrections FIXED, not asserted):

1. **The evaluator's printed "TRADEOFF-CONFIRMED" was reached by a broken branch** (skeptic catch). The frozen PREREG requires TRADEOFF to have *no* cell meet all three criteria; one cell, `(registered, q2=0.15)`, met all three in 7/8 seeds, so the literal frozen verdict is **PARTIAL/KNIFE-EDGE** (one cell → RAW 134 §12.1 negative), not TRADEOFF. The code's bare `elif rho<0` was more lenient than the frozen text; **fixed** in `p1c_run.py` (explicit "no passing cell" guard). TRADEOFF-CONFIRMED becomes the honest verdict *only after* the passing cell is disqualified on design grounds (below) — which the evaluator never computed.

2. **The passing cell is a double artifact (skeptic-predicted, then confirmed by two tests):**
   - **It was never the state the phase measures.** q2=0.15 at W=8 is qW=1.2 — *supercritical*; the "quench" regrows to the `ALIVE_CAP=30000` cutoff. The d_s=1.91 reading was taken on a ~31,000-node graph frozen at an arbitrary simulation cap, not the ~2,000-node stationary quench state PREREG_P1C intended. Its own shell classifier reads `exp` on 6/8 seeds (ê≈3.2) — expander, not manifold — **the two calibrated instruments disagree on the identical graphs** (they agree on all clean anchors).
   - **Test (a) — population-bounded rerun** (`ALIVE_CAP`→2500, same 5 seeds): d_s = 2.37–2.58 at **0.2–0.6% engagement**. At the intended size the state is *frozen and disengaged*, not engaged-2D; the "19% engagement, d_s 1.9" was a growth transient at 31k. The passing cell dissolves.
   - **Test (b) — d_s null:** a **random 4-regular graph at N=2025 reads d_s = 2.08** (torus2d anchor = 2.001); random 6-regular reads 0.67; random 4-regular at N=31k reads 5.16. **The d_s estimator, calibrated only on clean periodic lattices, cannot distinguish a 2D torus from a random 4-regular expander at N≈2000, and is wildly size-dependent.** The "2D band" [1.7, 2.3] admits expanders. The geometric criterion was invalid from the start.

3. **The tradeoff itself is real and is the result:** registered selector stays connected (LCC-frac = 1.00 everywhere) but its engagement is a monotone-decreasing function of q2 while d_s rises monotonically (q2 0.05→0.25: d_s 1.30→1.28→1.91→2.30→2.50; engagement 66%→79%→19%→4%→1%) — i.e. connected states are either engaged-but-low-d_s or high-d_s-but-frozen, never both. Non-descendant selector engages hard (22–83%) but fragments at every q2 (LCC-fraction ≈ 0.00–0.01, d_s undefined). Across the 10 cells, engagement and connectivity are anticorrelated (Spearman −0.54). **Directed selection strong enough to shape structure is strong enough to fragment it; the connected geometric phase is unreachable by cycle-closure selection under quench** — and even if a candidate appeared, the d_s instrument could not certify it at this scale.

## Skeptic review

| # | objection | resolution |
|---|---|---|
| 1 | Printed verdict violates its own frozen precondition (one cell met all three); code branch more lenient than PREREG. | **FIXED** — evaluator corrected; letter-verdict is PARTIAL/KNIFE-EDGE, upgraded to TRADEOFF only after the cell is disqualified on design grounds (Verdict 2). |
| 2 | Passing cell measured on a 31k `exp-explosion` graph frozen at ALIVE_CAP, not the intended ~2k quench state. | **CONFIRMED via test (a)** — bounded to ~2500 it reads d_s 2.4–2.6 at ~0.4% engagement; the engaged-2D reading was an explosion-size transient. |
| 3 | d_s vs shell classifier disagree on the passing graphs (d_s 1.9 vs cls exp 6/8). | **ACCEPTED as disqualifying** — instruments agree on all clean anchors; disagreement ⇒ not geometric. |
| 4 | d_s≈1.9 is a finite-window return-slope artifact on an expander, monotone in the spawn knob. | **CONFIRMED via test (b)** — random 4-regular reads d_s 2.08 at N=2025; the band admits expanders; d_s is size-dependent (5.16 at 31k). |
| 5 | KNIFE-EDGE clause was not in the frozen PREREG (retrofitted from RAW 134 §12.1). | **ACCEPTED** — recorded as a general principle applied post hoc, not a frozen gate; the frozen buckets are GEOMETRIC-SELECTION / TRADEOFF / PARTIAL, and this is PARTIAL-then-disqualified. |
| 6 | LCC-fraction gate discriminates nothing in the registered arm (always 1.0). | **ACCEPTED** — noted; the operative discriminator was d_s (invalid) and engagement (real). |
| 7 | Missing d_s null control — anchor set was clean lattices only. | **FIXED via test (b)** and banked: any future d_s-based gate MUST include a random-graph null in calibration (the connected-non-manifold control the P0 autopsy skeptic already flagged as missing). |

## What this proves / does not prove

- **Proves:** engagement and connectivity are anticorrelated under cycle-closure selection + quench (Spearman −0.54; the two selectors bracket it and no intermediate q2 escapes); the registered selector under quench is connected but its engaged regime is low-d_s and its high-d_s regime is frozen; the non-descendant selector fragments at every setting; **the d_s spectral-dimension estimator cannot certify 2D geometry at N≈2000, degree 4 — a random expander reads d_s≈2.0** (instrument finding, generalizes beyond this phase).
- **Does not prove:** that no directed dynamics can produce geometry (only cycle-closure selection under quench was tested, and the certifying instrument was shown inadequate); anything comoving (the comoving-growth phase of Addendum F §18.2 was not reachable — all reachable states were freeze, fragment, or explode); that a valid d_s gate would still return TRADEOFF (the gate was invalid, so the geometric question is *reopened*, not answered negative).

## Consequence for the arc (banked, no fresh run)

Exp 138 closes with: **geometry is selectable at equilibrium (P0), not by seed-grown directed branching (P1b, theorem-grade), not by quench + cycle-closure selection (P1c, tradeoff) — and the observer-side instrument that would certify emergent geometry (spectral d_s) fails its own random-graph null at these scales.** The last point is the sharpest: it is RAW 134 §5's wall reappearing on the *measurement* side (a merge/instrument reports the rank it is handed; on expander channels it returns garbage, here d_s≈2 on a random 4-regular graph — the Naor/Pope bound, Addendum §12.2, made concrete). Two banked prerequisites before any further geometrogenesis phase: (i) a d_s (or shell) instrument validated to separate manifold from expander at the working N and degree, with a random-graph null in the calibration set; (ii) a growth rule with a genuine comoving (polynomial-in-time, self-critical) regime, which neither seed-growth nor quench provided. Absent (i), no geometric PASS on this substrate is certifiable regardless of the dynamics.
