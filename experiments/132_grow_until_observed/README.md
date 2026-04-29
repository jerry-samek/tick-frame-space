# Experiment 132 — Grow Until Observed: Three-Layer Capacitor Substrate

**Status:** Scaffolded, not yet implemented.
**Theory:** [`docs/theory/raw/132_untested_capacitor.md`](../../docs/theory/raw/132_untested_capacitor.md)
**Predecessors (recent):**
- Exp 131_a (lineage_substrate) — RAW 131 first test, falsified
- Exp 131_b (anisotropic_connectors) — RAW 131 variant test, partial result with horizon-scaling failure
- Exp 133 (closed_loop_substrate) — closed-loop integer hold-and-fire, falsified for sustained fields
- Exp 134 (pattern_coherence) — CA-style renewal, locality confirmed, contact = decoherence

## Goal

Test the three-layer "grow until observed" substrate articulated in RAW 132 §5:

| Layer | What grows | Discharge |
|---|---|---|
| **Charging phase** (RAW 127) | Real charge level, 0–100% of threshold | Resets to Empty; emits quantum down all connectors |
| **Adaptive threshold** (RAW 132 §3.3) | Threshold value, slowly with firing history | Each discharge contributes to its own threshold growth |
| **Connector load** (RAW 132 §3.4) | Deposits in transit on each edge | Discharge releases load downstream |

Discharge is the only externally visible event, by hardware construction.

## What success looks like

The five-row outcome table from RAW 132 §6:

1. Test pattern dissolves on contact with planet field — capacitor doesn't rescue 134's contact-decoherence failure.
2. Test pattern stays coherent at distance but doesn't drift — field-without-force result.
3. Test pattern stays coherent and drifts toward planet — synthesis succeeds.
4. Drift profile matches Newton's 1/r² — first honest gravity from substrate.
5. Threshold(r) and connector-load(r) match GR's metric components — full Schwarzschild metric earned as substrate firmware.

Outcomes 3+ are partial wins; 5 is the ambitious target. Outcome 1 would close the discrete-substrate question with positive falsification.

## Scope (Phase 1)

Following RAW 132 §7's "smallest implementation that holds all five [components] together":
- **Substrate:** cubic lattice (debug-friendly), small (e.g., 30³ cells).
- **Test entity:** single K=4 renewal pattern (matching Exp 134 fixture F1 geometry).
- **Planet:** single K=4 renewal pattern, fixed position.
- **Three-layer machinery:** capacitor cell datatype, adaptive thresholds (§3.3), load-bearing connectors (§3.4).
- **Operational commitments per RAW 132 §3:** entity ≥ 50% sustained for ≥1 tick; deterministic threshold-firing; connectivity-baseline + use-driven adaptive threshold; load-driven connector propagation.

## Phases

1. **Phase 1 — vacuum self-coherence:** verify a single K=4 pattern is a fixed point under the three-layer mechanism with no planet present. Equivalent to Exp 134 Phase 1 sanity check, on the new substrate. Failure mode: rule's added complexity breaks vacuum invariance.
2. **Phase 2 — drift in planet field:** add the planet pattern, observe whether test pattern drifts toward it (Goal B from Exp 134 Phase 2 brainstorm), with the three-layer mechanism providing the long-range coupling that Exp 134 lacked.
3. **Phase 3 — quantitative match:** if Phase 2 shows drift, measure threshold(r) and connector-load(r) profiles around the planet; compare to GR's time-dilation factor and g_rr stretching.

## Implementation notes

This is scaffolding. Implementation is the next session's work.

The full design is in [RAW 132](../../docs/theory/raw/132_untested_capacitor.md) — §3 has the operational commitments, §5 has the synthesis mechanism, §7 has the implementation requirements. Read RAW 132 first; this README is just orientation.

## Files (planned)

```
experiments/132_grow_until_observed/
├── README.md                  # This file
├── capacitor.py               # Cell datatype + adaptive threshold dynamics
├── connectors.py              # Edge datatype + load-driven propagation
├── substrate.py               # Tick driver + connected-component analysis (port from Exp 134)
├── scenarios.py               # Phase 1/2/3 setup definitions
├── tests/                     # Unit tests for each module
├── phase1_test.py             # Vacuum self-coherence verification
├── phase2_test.py             # Drift observation
├── phase3_analysis.py         # Quantitative metric profile (if Phase 2 succeeds)
└── RESULTS.md                 # Outcome documentation
```

Status: `README.md` only. Everything else is to be built when the user is ready to start.
