# Phase 1a — coordinateless conserved-subdivision: CLEAN NEGATIVE (+ precise diagnosis)

Per PREREG A.6/A.4. Result: **no coordinateless memory-resonance rule produces a finite-dimensional space**, under either uniform refinement (Arm U) or capacitor firing (Arm F). The wall is **locality / a metric on the distinctions**, and it is localized empirically below.

## Arm U — uniform refinement × resonance rules (`phase1a_coordinateless_run.py`)
| rule | N | mean deg | diameter | d_s (depth 8→11) | flavor |
|---|---|---|---|---|---|
| hamming1 (hypercube) | 256→2048 | = depth | = depth (= log₂N) | 0.35→0.58→0.87→1.22 | **EXPANDER** (small-world, diam~logN) |
| mirror (prefix+complement) | 256→2048 | = depth | = log₂N | 0.35→…→1.22 | **EXPANDER** (identical to hypercube) |
| lastk=3 / lastk=5 (local) | — | — | — | — | **DISCONNECTED** (fragments: cc=8, cc=32) |

Global bit-flip resonance → expander (everything ~log N hops from everything = no locality). Local resonance → shatters into disconnected blocks. Neither is a manifold.

## Arm F — capacitor firing (difference = resonance degree; thresholds 4/8/16/32)
| threshold | N | deg | diam | d_s | depth spread |
|---|---|---|---|---|---|
| 4 / 8 / 16 / 32 | 1024 | 10.0 | 10 | 0.87 | **d[10–10]** (uniform) |

**Identical at every threshold, and identical to Arm U's hamming1 depth-10 row.** The capacitor degenerated to uniform refinement: a symmetric address space gives every cell the same resonance degree → identical charging → lockstep firing. Threshold shifts *when* all fire, never *which*. **Solipsism null confirmed empirically:** a single symmetric stream + capacitor → lockstep → expander, not geometry.

## Diagnosis (the valuable part — bulletproof and empirical)
**The wall is LOCALITY, not dimension.** An address space under "flip one distinction" is intrinsically a hypercube — any distinction can flip, so any two memories are ~log N apart (an expander). Finite-dimensional locality would require a **neighborhood structure on the distinctions** ("these distinctions are near, those far") — and *that neighborhood structure is the geometry we refused to assume*. The capacitor cannot manufacture it, because a **closed, symmetric, single-origin substrate has no differential-difference source** to break lockstep (a local difference measure on a symmetric space is uniform — measured: `d[10-10]` at all thresholds).

This unifies the session's threads with running code:
- Confirms the **solipsism** diagnosis (symmetric single stream → lockstep → no structure).
- Same root cause as **Exp 132's uniform saturation** (closed symmetric substrate, no difference source).
- Matches the **literature** (Trugenberger: local no-target rule → d=1; no local rule reaches integer-d without a global/foliation or fixed building-block).
- Concrete form of "**everything goes back to the one we must assume**": to get finite-d you must assume EITHER a metric on the distinctions (the geometry) OR a symmetry-breaking source — and the bare substrate gives neither (random would = no structure; structured = assumed).

## Per PREREG A.4 (program falsifier): CLEAN NEGATIVE — STOP this rule class
The coordinateless conserved-subdivision rule class (uniform or capacitor, symmetric origin, bit-flip resonance) does **not** yield a finite-dimensional space. No reframe. The next attempt must **surrender a named commitment**: introduce a principled **symmetry-breaking / metric-on-distinctions**. Two candidates:
1. **Trit-3 (RAW 108):** give the distinctions a 3-fold neighborhood structure (Same/Different/Unknown as 3 local directions) — the framework's own candidate for "3 from the trit." Test: does a 3-structured distinction-space yield d≈3?
2. **Explicit minimal scaffold:** assume a metric on the distinctions (the thing we avoided), test whether the *dynamics* (consumption/growth/gravity) live correctly on it — trading emergent-dimension for emergent-dynamics.

Status: Phase 1a complete. Honest negative, precisely localized. Decision (which commitment to surrender) is the user's.
