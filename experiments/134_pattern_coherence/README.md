# Experiment 134: Pattern Coherence (Phase 1)

See `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md` for the
full design and rationale, and `RESULTS.md` for the Phase 1 outcome.

## Run

```bash
# Full sweep (unit tests + Phase 1 deliverable)
pytest experiments/134_pattern_coherence/ -v

# Phase 1 deliverable only (bit-identity over 10,000 cycles per fixture)
pytest experiments/134_pattern_coherence/phase1_test.py -v -s
```

## Status

Phase 1: see `RESULTS.md`.
Phase 2 / Phase 3: not yet started; design sketches in the spec.
