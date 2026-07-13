# Experiment 132 — Grow Until Observed: Three-Layer Capacitor Substrate

**Theory:** [`docs/theory/raw/132_untested_capacitor.md`](../../docs/theory/raw/132_untested_capacitor.md) (RAW 132)
**Phase 1 spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-design.md)
**Phase 1 plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md)
**Phase 2 spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md)
**Phase 2 plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md)
**Phase 2A.5 spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-phase2a5-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-phase2a5-design.md)

**Predecessors (recent):**
- Exp 131_a (lineage_substrate) — RAW 131 first test, falsified
- Exp 131_b (anisotropic_connectors) — RAW 131 variant, partial result
- Exp 133 (closed_loop_substrate) — closed-loop integer hold-and-fire, falsified
- Exp 134 (pattern_coherence) — CA renewal, vacuum coherent but no field-at-distance

## Run

```bash
# Full test sweep
pytest experiments/132_grow_until_observed/ -v

# Phase 1 deliverable (5000-cycle vacuum sustainment)
pytest experiments/132_grow_until_observed/phase1_test.py -v -s

# Phase 2 deliverable (planet + test + 4-hypothesis post-hoc analysis)
pytest experiments/132_grow_until_observed/phase2_test.py -v -s

# Phase 2A.5 deliverable (3-run superposition test: R1 planet-only, R2 test-only, R3 combined)
pytest experiments/132_grow_until_observed/phase2a5_test.py -v -s
```

## Status

- **Phase 1 (vacuum self-coherence):** **PASS** — see [`RESULTS_phase1.md`](RESULTS_phase1.md). K=4 cycle sustained for 5,000 cycles; tuning analysis shows the working region has predictable structure (two derivable constraints), not fragile single-point tuning.
- **Phase 2 (drift in planet field):** **HONEST NEGATIVE** — three of four hypotheses NOT SUPPORTED at this parameter set (H3.5 and H4.1 falsified; H5.1 not supported; H5.x panel collapsed onto H5.1 and is therefore inconclusive). See [`RESULTS_phase2.md`](RESULTS_phase2.md) for detail.
- **Phase 2A.5 (three-run superposition test):** **OUTCOME 3 (superposition fails)** — see [`RESULTS_phase2a5.md`](RESULTS_phase2a5.md). χ² thresholds = 0.169, χ² loads = 0.168 (both > 0.1). **Key diagnosis: substrate saturation.** R1 (planet-only, no test pattern present) shows perfectly flat threshold(r) = 100.05 and load(r) = 1.0 at every radius — Phase 2's flat profiles were not test-pattern contamination but a substrate property at these parameters. H5.7 (self-subtracting reading) is operationally untestable here because R1 has no field structure to recover.
- **Phase 3 (GR metric profile):** deferred until at least one of {threshold(r), load(r)} produces non-flat structure with R1 alone. Highest-priority next experiments are Phase 2A.2 (load_coefficient sweep) and Phase 2A.4 (partial connectivity), which target the saturated regime directly.

## Three-layer mechanism

| Layer | What grows | Discharge |
|---|---|---|
| Charging phase | Real charge level, 0 → threshold | Resets to 0; emits deposits to all connectors |
| Adaptive threshold | Threshold value, slowly with firing history | Each discharge raises threshold by adaptation amount |
| Connector load | Deposits in transit on each edge | Discharge releases deposits into connectors |

Phase 1: `load_coefficient = 0` (mechanism implemented and unit-tested, not exercised in deliverable).
Phase 2: `load_coefficient = 0.1` (mechanism active; load(r) profile measured — found flat).
