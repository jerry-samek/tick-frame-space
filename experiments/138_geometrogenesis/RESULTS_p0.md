# Exp 138 Phase P0 — RESULTS: condensation positive control

**Dates:** 2026-07-10 (launch) → 2026-07-11 (kill/resume, gate, skeptic pass, autopsy, this doc).
**Pre-registration:** `PREREG_P0.md` (frozen after G-I0, before the engine ran; declared deviations all pre-freeze/pre-production).
**Code/data:** `p0_condensation.py`, `p0_resume.py`, `p0_autopsy.py`; `results_p0_console.txt`, `results_p0_resume_console.txt`, `results_p0_spotcheck_console.txt`, `results_p0_autopsy_console.txt`; `results/p0.json`, `results/p0_autopsy.json`, `results/p0_condensed_J4_s1000.json`.

## Verdict

**Gate G-P0: PASS, exactly as registered.** J ∈ {0.5, 1, 2}: 0/30 seeds `poly` (all `exp`); J ∈ {4, 8}: 20/20 `poly`. The classifier's flip sits between J=2 and J=4; the escape hatch was not needed. Both preconditions for P1 hold at sign level: a square-condensed phase is dynamically reachable in graph dynamics, and the frozen I0c instrument detects it.

**Skeptic-corrected scope (each item below is FIXED or ACCEPTED in the ledger):**

1. **What the condensed phase IS (autopsy, post-skeptic):** the J=4 seed-1000 final graph is a **single connected component** (diameter 16), every vertex participates in ≥1 square, 54% of vertices have square-lattice-local 1-balls, spectral dimension 1.56 vs same-size anchors (tube C64×C4: 1.01; torus2d(16): 1.76; true 2D at N→∞: 2.0), instrument reading ê = 1.257 ± 0.021 stable in 99/100 independent source draws vs anchors torus2d 1.000 / tube 0.160 / triangle-free RRG 2.09-`exp`. Honest description: **a partially crystallized, 2D-leaning square mosaic — connected, not a tube, not fragmented, not a finished crystal.** "Emergent 2D geometry" remains too strong; "square-condensed mosaic in the 2D direction by every anchor" is earned.
2. **The runs end arrested, not equilibrated.** Energy still declining at sweep 1500 in every condensed run; late-run acceptance ~0.1–0.3% (NOT the ~1–2% earlier stated); classification flip-flops along the trajectory (up to 17 times in one run) — the endpoint is a sample of a still-relaxing glassy state. A5 shows the flips are dynamics, not source-sampling (99/100 stability on the final state). The gate result is a statement about *reachability of the condensed regime within 1500 sweeps*, not about equilibrium.
3. **Near-boundary honesty (mandatory PREREG_I0c flag, initially omitted — skeptic catch):** 13/18 fresh condensed finals and ALL 18 fresh sweep-0 disordered readings have |R² gap| below the frozen control_margin (0.0258); the low-J arm's margins were never recorded (console splice lacks r2_gap). **The entire P0 classification operates inside the instrument's fragility zone at N=256**; the result is carried by sign + seed replication (0/30 vs 20/20) + the autopsy anchors, not by per-reading margins.
4. **Splice validated:** the 2026-07-11 01:15 kill (machine sleep) left 32/50 finals recorded on console; 18 cells re-run; the spot-check (full deterministic regeneration of J=4 seed 1000) reproduced the recovered console line exactly (cls=poly, ê=1.26, sq/edge=0.479).
5. **"Sharp transition" downgraded:** underlying observables are a smooth crossover (ê 2.03→1.97→1.72→1.20→1.12; sq/edge 0.03–0.06 → 0.49 → 0.53 across the ladder); one size, no hysteresis, no finite-size scaling. What is sharp is the classifier's flip, at factor-2 J resolution.
6. **Energy bookkeeping exact in practice:** radius-1-ball ΔH drift = exactly 0.0 at every checkpoint of all 18 fresh runs (final-checkpoint-only for the 32 recovered).

## Skeptic review

| # | objection | resolution |
|---|---|---|
| 1 | Mandatory near-boundary flags silently dropped; both arms sub-margin. | **FIXED** — Verdict 3; flags in this doc; detection acknowledged as sub-margin, carried by sign+replication+anchors. |
| 2 | Low-J arm margins unrecoverable from console splice. | **ACCEPTED** — recorded as a permanent gap for the 32 recovered runs; the spot-check validates the splice mechanism itself. |
| 3 | "Drift exactly 0" verified only for fresh runs. | **ACCEPTED** with scope stated (Verdict 6). |
| 4 | Endpoint of a fluctuating classifier; flip-flops untraced. | **FIXED via A5** — final-state classification is source-stable (99/100); flips are relaxation dynamics; arrested-state framing adopted (Verdict 2). |
| 5 | Not equilibrated; "condensation completed" unsupported; acceptance misquoted. | **FIXED** — Verdict 2 wording; acceptance corrected to 0.1–0.5%. |
| 6 | No condensed graph ever inspected; disconnection could mimic poly. | **FIXED via autopsy A1–A6** — single component, diameter 16; tube and fragmentation nulls dead; mosaic census reported (Verdict 1). |
| 7 | "Consistent with Kelly-Trugenberger emergent 2D" overstated; ê extrapolated below calibration size. | **FIXED** — replaced by anchor-relative statement (Verdict 1); torus3d's own reading (1.756 for true 2.0) quoted as the instrument's known bias. |
| 8 | Splice determinism untested; two fast J=8 cells suspicious. | **FIXED** — exact-match spot-check (Verdict 4); fast cells explained as final uncontended pool wave, and determinism now demonstrated. |
| 9 | J=8 ê < J=4 ê untraced. | **ACCEPTED** open — consistent with deeper-quench arrest; not load-bearing for the gate. |
| 10 | Stale Jost-Liu docstring in curvature.py. | **FIXED** in code. |
| 11 | P1 launched on G-P0 before the P0 skeptic pass. | **ACCEPTED** as a process deviation — parallelization choice; P1's own gate+skeptic protect its conclusions; had the P0 skeptic voided the gate, P1 would have been halted and re-gated. Logged. |
| 12 | Long-run equilibration test (5–10k sweeps) not run. | **ACCEPTED** as priced future work; the gate as registered is a reachability claim and does not require equilibrium. |

## What this proves / does not prove

- **Proves (sign level, N=256, k=4, hard-core, exact-κ action):** the disordered triangle-free RRG phase and a square-condensed connected mosaic phase are both dynamically reachable; the transition in the classifier's reading is seed-replicated 30/30 vs 20/20 across a factor-2 coupling ladder; the frozen instrument separates the endpoints (sub-margin per reading, anchored structurally by the autopsy). The P1 preconditions hold.
- **Does not prove:** equilibrium phase structure; sharpness in the statistical-mechanics sense; "emergent 2D geometry" (the mosaic is 2D-leaning by anchors, 54% locally crystalline, arrested); anything at other N, k, or actions; numeric replication of published Kelly-Trugenberger curves (sign-level only, per PREREG).
