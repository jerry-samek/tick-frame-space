# Experiment 133 — Closed-Loop Graph Substrate

Substrate orbital mechanics from a closed-loop, conservation-respecting,
differential-only graph dynamics. Cells hold integer energy, see only
differences, and fire when integer math allows. No `+1/tick`, no entity labels,
no coordinates in the substrate.

See spec: `docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md`

## Quick start

```bash
# Sanity (fast)
python -u phase1_sanity.py

# Field formation (~10 min on 100k nodes)
python -u phase2_static_star.py

# Gradient response (~5 min)
python -u phase3_test_pattern.py

# The goal — orbit
python -u phase4_orbit.py

# Stretch goal — emergent orbit
python -u phase5_emergent.py
```

## Phases

1. Conservation + diffusion sanity
2. Static star, 1/r² field formation
3. Test pattern in field (gradient response)
4. Orbit (Keplerian, with seeded tangential bias)
5. Emergent orbit (no seeded bias) — stretch goal

Success criteria and falsification per spec §5 and §8.
