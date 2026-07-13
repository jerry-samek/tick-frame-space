# Experiment 134: Pattern Coherence

See:
- `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md` (Phase 1 spec)
- `docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md` (Phase 2 spec)
- `RESULTS.md` (Phase 1 outcome)
- `RESULTS_phase2.md` (Phase 2 outcome)

## Run

```bash
# Full test sweep (all phases)
pytest experiments/134_pattern_coherence/ -v

# Phase 1 deliverable
pytest experiments/134_pattern_coherence/phase1_test.py -v -s

# Phase 2 deliverable
pytest experiments/134_pattern_coherence/phase2_test.py -v -s
```

## Status

Phase 1: see `RESULTS.md`.
Phase 2: see `RESULTS_phase2.md`.
Phase 3 (opposite-sign annihilation): not yet started.
