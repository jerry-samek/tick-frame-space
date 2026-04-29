# Experiment 132 — Grow Until Observed: Three-Layer Capacitor Substrate

**Theory:** [`docs/theory/raw/132_untested_capacitor.md`](../../docs/theory/raw/132_untested_capacitor.md) (RAW 132)
**Spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-design.md)
**Plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md)

**Predecessors (recent):**
- Exp 131_a (lineage_substrate) — RAW 131 first test, falsified
- Exp 131_b (anisotropic_connectors) — RAW 131 variant, partial result
- Exp 133 (closed_loop_substrate) — closed-loop integer hold-and-fire, falsified
- Exp 134 (pattern_coherence) — CA renewal, vacuum coherent but no field-at-distance

## Run

```bash
# Full test sweep
pytest experiments/132_grow_until_observed/ -v

# Phase 1 deliverable (5000-cycle sustainment)
pytest experiments/132_grow_until_observed/phase1_test.py -v -s
```

## Status

- **Phase 1 (vacuum self-coherence):** **PASS** — see [`RESULTS_phase1.md`](RESULTS_phase1.md). K=4 cycle sustained for 5,000 cycles; tuning analysis shows the working region has predictable structure (two derivable constraints), not fragile single-point tuning.
- **Phase 2 (drift in planet field):** not yet started.
- **Phase 3 (GR metric profile):** not yet started.

## Three-layer mechanism

| Layer | What grows | Discharge |
|---|---|---|
| Charging phase | Real charge level, 0 → threshold | Resets to 0; emits deposits to all connectors |
| Adaptive threshold | Threshold value, slowly with firing history | Each discharge raises threshold by adaptation amount |
| Connector load | Deposits in transit on each edge | Discharge releases deposits into connectors |

Phase 1: `load_coefficient = 0` (mechanism implemented and unit-tested, not exercised in deliverable).
Phase 2: turns it on.
