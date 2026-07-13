# Exp 136 — Conserved-Subdivision Substrate — CLOSURE

**Status:** CLOSED 2026-06-05 with a **clean, well-localized negative.** Consolidated by user decision (stop here, don't open a new sub-quest).
**Idea tested:** Tom's "time = wrapping / division" — does a conserved-subdivision substrate, read leaf→root, yield emergent 3D space (and, downstream, motion/gravity/GR/QM)?
**Verdict:** Emergent dimension from a local, conserved, symmetric, coordinateless subdivision substrate is **blocked — by a locality wall, not a dimension-selection failure.** The reason is precise and unifies the whole arc.

---

## What was built and run
- **Phase 0** (`substrate.py`, `battery.py`, `nulls.py`, `PREREG.md`): a calibrated measurement battery (Hausdorff, spectral-dim, loop-density, Ollivier-Ricci via POT, gudhi Betti) that provably **separates 3D / 2D / tree / blob** (calibration gate passed, 25/25 tests). Two honest calibration findings frozen: graph dimension estimators read ~0.5 low → WIN is **benchmark-relative** (spec §9); Ollivier-Ricci flags positive-curvature/flatness, **not** sparse trees (tree detection = spectral + loops). Bare all-glue baseline = **exactly K_N** (gluing is foundational).
- **Phase 1a** (`coordinateless.py`, `phase1a_coordinateless_run.py`, `RESULTS_phase1a.md`): the substrate rebuilt **coordinateless** per the reframe (below). Cells = addresses (replayed memory); edges = memory-resonance; dimension = measured intrinsic d of the woven graph. Ran **Arm U** (uniform refinement × resonance rules) and **Arm F** (capacitor-driven async firing).

## The clean negative (empirical, decisive)
- **Arm U:** global bit-flip resonance (hamming1 / mirror) → **EXPANDER** (diameter ~ log N, no locality); local resonance (lastk) → **DISCONNECTED** fragments. No finite d>1.
- **Arm F:** capacitor **degenerated exactly onto uniform** — depth spread `d[10-10]` at every threshold (4/8/16/32), identical to Arm U's hamming1 row. A symmetric address space → uniform resonance degree → lockstep firing. Threshold shifts *when* all fire, never *which*. **Solipsism confirmed by measurement.**

## The diagnosis (the contribution)
**The wall is LOCALITY, not dimension.** Under "flip one distinction," an address space is intrinsically a hypercube — any two memories are ~log N apart (an expander). Finite-dimensional locality requires a **neighborhood structure on the distinctions** ("these are near, those far"), and *that structure is the geometry we refused to assume.* A closed, symmetric, single-origin substrate has **no differential-difference source** to break the symmetry, so the capacitor cannot manufacture locality — it fires in lockstep.

This unifies the session's threads with running code:
- Confirms the **solipsism** insight (symmetric single stream → lockstep → no structure).
- Same root cause as **Exp 132's uniform saturation** (closed symmetric substrate, no difference source).
- Matches the **literature** (Trugenberger: local no-target rule → d=1; no local rule reaches integer-d without a global foliation or a fixed building-block — CDT/NGF).
- The concrete content of "**everything goes back to the one we must assume**": finite-d requires assuming EITHER a metric on the distinctions (the geometry) OR a symmetry-breaking source. The bare substrate supplies neither (random → no structure; structured → assumed).

## The reframe that this experiment earned (keep this)
Dimension is **not a property of the substrate.** The substrate is information — a connection-graph. Dimension is the **observer's read = the graph's intrinsic dimension** (relational realism, *not* idealism: the graph is objectively real, its dimension is an objective relational property, *read* not *invented* — which keeps it falsifiable). Asking "what makes the substrate 3-dimensional" was a category error; the honest question is "what intrinsic dimension does the connection-structure have, and what would give it locality." Also settled: **assume the observer (functional trit/comparison), not consciousness** (qualia stay the open hard problem, never a premise — `project_observer_not_consciousness`).

## Why this closure is itself the point
The 118–135 arc failed by **reframing every negative into one-more-untested-layer.** Here we hit a negative and did **not** do that. Per the program falsifier **pre-registered before running** (PREREG A.4), we accepted the clean negative, localized it precisely, and let it **name the commitment that would have to be surrendered to continue.** That discipline — not the dimension result — is the win of this experiment.

## Parked (NOT pursued now; for a future session)
To go further, one named commitment must be surrendered (A.4). Two candidates, each needing a design pass first (no build-before-spec):
1. **Trit-3 / RAW 108:** surrender strict symmetry — give the distinctions a 3-fold neighborhood structure (Same/Different/Unknown as 3 local directions) and measure whether d→3. The sharpest falsifiable test of the framework's deepest claim (assume the trit, derive the dimension). Caveat: a 3-fold local rule is not guaranteed to give 3D.
2. **Minimal-geometry + dynamics:** surrender emergent-geometry — accept a minimal given relational geometry and test whether the *dynamics* (growth/consumption → gravity, equivalence-principle "push up") live on it. Reconnects to the one ratified earned result (128 v11: 1/r² on a given RGG, R6) and to the original physical vision.

## Earned, kept
The calibrated battery (Phase 0) is reusable and trustworthy. The relational-dimension reframe and the observer-not-consciousness boundary are durable framework commitments. The locality-wall diagnosis is a real result that any future emergent-geometry attempt must confront.
