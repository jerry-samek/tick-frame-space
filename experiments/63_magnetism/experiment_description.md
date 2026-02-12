# Discrete Altermagnetism Experiment — v2

**Date**: February 12, 2026
**Status**: Implemented (v2 with three modes)

## Objective

Test whether the tick-frame gamma substrate independently discovers altermagnetism from pure discrete rotation dynamics.
Altermagnetism is the "third type" of magnetism: zero net magnetization but anisotropic directional transport. If the
discrete substrate reproduces this from integer rotations + lag + lattice geometry alone, it validates the substrate as
genuine discrete physics.

**Critical constraint**: Pure discrete operations only. No continuous math, no pi, no floating-point angles. Integer
rotations, 8-step cycle, all direction vectors in {-1, 0, +1}.

## v1 Problem

The original experiment (equilibrate -> freeze field -> probe) revealed a fundamental flaw: the time-averaged tangential
deposit from a rotating entity is exactly zero. Over one 8-tick cycle, every direction gets exactly one deposit
regardless of CW/CCW sign or lag value. After many full cycles, the field is a symmetric radial well with no
pattern-level tangential signal. M_net and max_W_tang values were identical across all four patterns.

## v2 Fix: Three Modes

### Mode: `frozen` (baseline)

Original approach. Equilibrate with unsigned gamma deposits, freeze field, probe on frozen field. Expected to fail —
serves as reference showing the problem.

### Mode: `signed` (Approach B — Signed Tangential Field)

Adds a separate **signed tangential field** (`tang`) to `GammaField`. The deposit sign depends on omega handedness:
`tang += W_tang * omega` (positive for CW, negative for CCW). This breaks the cycle-symmetry that makes CW and CCW
indistinguishable in time-average.

- Center deposits go to `gamma` (radial well, same as before)
- Tangential deposits go to `tang` field (signed, preserves handedness)
- Gradient combines both: probes feel gravity from gamma + magnetic force from tang
- M_net computed from tang field sum directly (not gradient decomposition)

### Mode: `live` (Approach A — Live-Field Probing)

Probes move through the **actively evolving** field rather than a frozen snapshot. The CW/CCW difference exists within
each rotation sub-cycle as transient interference patterns. Probes must move through the live field to experience this.

- Phase 1: warmup (500 ticks, entities only)
- Phase 2: live probing (entities AND probes simultaneously)

## Test Patterns (4x4 entity arrays, omega = integer steps/tick)

| Pattern               | Layout              | Expected (signed mode)                                |
|-----------------------|---------------------|-------------------------------------------------------|
| **Checkerboard**      | Alternating +1/-1   | M_net = 0, d-wave tang pattern, anisotropic transport |
| **Stripe**            | 2x2 blocks of +2/-2 | M_net = 0, g-wave tang pattern, different anisotropy  |
| **Ferromagnetic**     | All +1              | M_net >> 0, uniform positive tang                     |
| **Antiferromagnetic** | Rows of +1/-1       | M_net = 0, stripe tang pattern                        |

## Success Criteria

### Signed mode (must pass):

- Compensated magnetism: M_net/M_net_ferro < 0.01 for checker/stripe
- Anisotropic transport: |A_NS| > 0.1 OR |A_EW| > 0.1 for checker/stripe
- Ferromagnetic: M_net >> 0
- Pattern specificity: checkerboard and stripe produce distinct results

### Live mode (must pass):

- Velocity dependence: faster probes deflect MORE (magnetic, not gravitational)

### Frozen mode (informational):

- All criteria reported but not scored (expected to fail)

## Running

```bash
# Full experiment — all three modes (5 runs per pattern per mode)
python experiments/63_magnetism/magnetism_experiment.py

# Smoke test (~2 min)
python experiments/63_magnetism/magnetism_experiment.py --smoke

# Single mode only
python experiments/63_magnetism/magnetism_experiment.py --mode signed

# Custom parameters
python experiments/63_magnetism/magnetism_experiment.py --runs 10 --eq-ticks 2000 --probe-ticks 4000
```

Output goes to `experiments/63_magnetism/results/`:

- Field heatmaps per mode per pattern (with tang field for signed mode)
- Probe trajectory plots per mode per pattern
- Fourier symmetry plots per mode per pattern
- Per-mode summary comparison bar charts
- Cross-mode comparison plot (`mode_comparison.png`)
- Velocity dependence comparison (`velocity_comparison.png`)
- `experiment_report.txt` and `experiment_results.json`
