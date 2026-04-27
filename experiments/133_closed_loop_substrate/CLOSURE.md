# Experiment 133 — Closure

**Started:** 2026-04-26
**Closed:** 2026-04-26 (same day)
**Branch:** `feature/exp-133-closed-loop-substrate`
**Spec:** `docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md`
**Plan:** `docs/superpowers/plans/2026-04-26-closed-loop-graph-substrate.md`

## Goal

Substrate orbital mechanics from a closed-loop, conservation-respecting,
differential-only graph substrate, without smuggling Newton, Kepler, or
any geometric ansatz. The hold-and-fire integer rule with wake bias was
the candidate.

## Phase outcomes

| Phase | Setup | Result |
|-------|-------|--------|
| 1 — Conservation/diffusion sanity | N=50k, α∈{0,1}, 1000 ticks | **PASS** — conservation invariant held across 2000 ticks; std stable at α=0; max_E bounded at α=1 |
| 2 — Static star, closed-loop | N=100k, α=1, 10k ticks | **FAIL** — slope=−0.012, r²=0.008. Field is flat. |
| 2b — Slope at intermediate ticks | Same as 2, slope at every snapshot | **FAIL** — slope ≈ 0 at every tick from 10 to 10000. No 1/r² transient anywhere. Substrate-too-small hypothesis falsified. |
| 2c — α sweep (closed-loop) | α ∈ {3, 5, 10}, 2000 ticks each | **FAIL** with diagnostic finding: slope went **positive** (anti-gravity). At α=5, slope=+0.165 with r²=0.71 at tick 100. Stronger wake bias drives energy outward; without a sink it accumulates at boundary → inverted gradient. |
| 2d — Source + absorbing boundary | star held fixed, r > 0.45 zeroed, α∈{0,1} | **SUCCESS** — radial gradient appears. α=0: ρ ∝ r^(−0.99) at tick 2000 (r²=0.96). α=1: ρ ∝ r^(−0.83) (r²=0.98). |
| 2e — Raw per-cell gradient | Phase 2d state, compute \|∇E\| per cell | **FAIL** — magnitude slope=−0.10, cos(angle to star)=+0.087. Per-cell gradient dominated by noise from integer quantization + RGG randomness. |
| 2f — Smoothed gradient | k-hop neighbor averaging before gradient | **PARTIAL SUCCESS** — coherent attractive radial field emerges with smoothing. At k=10: slope=−0.65, r²=0.50, cos=+0.48. Direction is attractive at every tested radius. But exponent is **not Newton's −2**. |
| 3b — Test pattern drift | Phase 2d setup + small planet | **FAIL** — planet dissipates from 605 to ~20 quanta within 400 ticks. Centroid bounces around seed location due to clustering noise picking up transient concentrations. No clean drift signal. |
| 3, 4, 5 — Original closed-loop drivers | Written but not run | Skipped — Phase 2 falsification of closed-loop conservation made these meaningless. Drivers committed for posterity. |

## What was earned

1. **Exact integer-arithmetic conservation in a vectorized tick rule.**
   The largest-remainder-with-residue-holding distribution preserves total
   energy exactly across every tick. Verified across N up to 100k, ticks
   up to 10000, and α from −1.5 to 10⁶. (16 unit tests, 200-tick stress
   test in code review.)
2. **Phase 1 stability.** Closed-loop dynamics with random initial energy
   stay statistically uniform at α=0; no runaway concentration at α=1.
   Substrate doesn't blow up.
3. **Source/sink restores radial structure.** With star held at fixed E
   and outer shell zeroed each tick, ρ(r) profile fits a clean power law
   (r²=0.96–0.98) at every tested α. Conservation must be **broken
   locally** for sustained gravity to exist — confirmed.
4. **Smoothed gradient is coherent and radially attractive.** With k=10
   neighbor-averaging, the force field on a test pattern points toward
   the star at every interior radius. cos(θ) climbs from 0.087 (raw) to
   0.48 (smoothed); near r ≈ 0.03 individual bins reach cos ≈ 0.86.
   A coherent gravitational direction exists at scale.

## What was falsified

1. **Strict closed-loop conservation in a finite substrate is incompatible
   with sustained radial fields.** Phase 2 ran 10000 ticks with no flux
   imbalance ever forming → flat field, slope ≈ 0. This is structural,
   not parameter-tunable: at every α tested in {0, 1, 3, 5, 10}, no 1/r²
   gradient appeared in pure conservation. With α≥3 the gradient inverted
   (anti-gravity). The "lossy reconstruction creates field" claim of
   spec §6 needs an exit channel — the loss must actually leave.
2. **The hold-and-fire integer rule does not produce Newton's −2 exponent.**
   Even with source/sink restored, the smoothed-gradient slope converges
   to about −0.65, not −2. 128 v11 with pure-real-valued propagation got
   −1.968 on the same RGG topology. The integer quantization + threshold
   firing produces a different macroscopic exponent — confirmed
   sub-Newton power law.
3. **Renewal-not-identity orbital mechanics not demonstrated dynamically.**
   Test patterns (planets) in any setup dissipate within ~400 ticks under
   the rule, faster than they can drift through the field. The
   centroid-tracking approach catches noise rather than motion.
4. **Spec §8 falsification matrix's row "Phase 2 fails (slope ≠ −2) →
   topology issue" is wrong** for our case. 128 v11 earned −1.968 on
   the same RGG with pure-propagation; topology is fine. The issue is
   rule design.

## Diagnostic mechanism

Why does our rule produce slope −0.65 (smoothed gradient) instead of
−2 like 128 v11?

- **Integer quantization** discretizes flow into per-edge integer chunks.
  At low E (cells with E < degree), most edges receive 0 quanta and the
  cell holds residue. This buffers flow at intermediate distances.
- **Wake bias**, while it helps near the star, does not steepen the
  far-field exponent (we saw α=0 give slope −0.99 in density vs α=1's
  −0.83 — without bias is actually steeper at far distances).
- **Noise dominates per-cell gradient.** Phase 2e showed raw \|∇E\| has
  r²=0.013 against radius — the macro profile is smooth-on-average but
  microscopically noisy. A test pattern smaller than ~5 hops cannot
  average noise enough to feel a coherent force.
- 128 v11 used pure-real propagation: `ρ_new[neighbor] += ρ[node] / degree[node]`.
  No quantization, no residue holding, no buffering. That gave −1.968.

## Per-experiment ontological learning

- **Conservation as a commitment**: the spec listed it as load-bearing.
  In finite substrates without sinks, it forces flat-field equilibrium.
  Real physics conserves energy globally but radiation effectively never
  returns on observable timescales — i.e., the universe is *so big* that
  the boundary is irrelevant. We can't recreate that on 100k cells.
- **The "lossy reconstruction = consumption = field" identity** holds
  *only when the loss can leave*. Local cell-residue-holding in a closed
  finite substrate doesn't produce field — the held energy just sits and
  re-emits.
- **Renewal-not-identity at the cell level** is real and works
  (Phase 1). At the entity level (a coherent pattern of cells), it
  remains unobservable: patterns dissipate too fast in the
  integer-quantized regime.
- **Direction of gradient flips with strong wake bias.** At α≥3 in pure
  conservation, the substrate creates anti-gravity — wake bias prevents
  return flow so heavily that energy accumulates at the boundary. With
  a sink this would restore gravity; without it, anti-gravity is the
  natural outcome.

## Spec sections that need revision

- §2 commitment 1 (Conservation): the spec asserts "every tick
  *restructures* a fixed pool" with no source or sink. **Falsified for
  finite substrates.** A revision should either:
    - Drop strict conservation (allow boundary to be a sink, like real
      cosmological horizons act practically as sinks)
    - Or commit to *infinite* substrate (which we can't actually
      simulate)
- §6 commitment 6 (Lossy reconstruction = consumption): the loss must
  have **somewhere to go**. The spec's framing was incomplete.
- §8 falsification matrix: row "Phase 2 fails (slope ≠ −2) → topology
  issue" is incorrect for our rule. Should be "rule-design issue
  (quantization, threshold firing)".
- §3.1 graph construction: RGG + sink at boundary is fine; the rule is
  the load-bearing thing.

## Files

```
experiments/133_closed_loop_substrate/
├── README.md                   # quick-start docs
├── substrate.py                # core: build_rgg, init_state, tick (vectorized, integer-exact)
├── metrics.py                  # per_tick_summary, cluster_high_energy
├── visualization.py            # radial_density_profile, fit_loglog_slope, plotters
├── tests/test_substrate.py     # 16 unit tests, all pass
├── phase1_sanity.py            # PASS — conservation + diffusion sanity
├── phase2_static_star.py       # FAIL — closed-loop static star
├── phase2b_transient_slope.py  # FAIL — no 1/r² transient
├── phase2c_alpha_sweep.py      # FAIL — closed-loop α sweep
├── phase2d_with_sink.py        # SUCCESS — source+sink yields radial structure
├── phase2e_gradient_field.py   # FAIL — raw per-cell gradient is noise
├── phase2f_smoothed_gradient.py # PARTIAL — smoothed gradient coherent but slope ≠ -2
├── phase3_test_pattern.py      # closed-loop driver, not run
├── phase3b_drift_with_sink.py  # FAIL — test pattern dissipates faster than drift
├── phase4_orbit.py             # closed-loop driver, not run
├── phase5_emergent.py          # closed-loop driver, not run
├── results/                    # logs, JSONs, PNGs (gitignored — use git add -f)
└── CLOSURE.md                  # this file
```

## Next-experiment prompt

The right next move is **not** to keep tuning this rule. The deeper
question is: **what minimal substrate dynamics produce coherent radial
flow with a Newton-shaped gradient AND support patterns that survive
many ticks?**

Two lines worth pursuing separately, possibly in parallel:

1. **Real-valued diffusion with source/sink (replicate 128 v11 cleanly).**
   Drop integer quantization. Allow fractional flow per edge. With
   pure conservation + sink at boundary, this should give slope −1.968
   (matching 128 v11 Phase 1). Then test whether cells act as integer
   capacitors *only when threshold is crossed* — capacitor model with
   real-valued field beneath. Hybrid integer/real.

2. **Pattern-as-renewal frontier (the Doc 28 honesty problem).**
   Even if the substrate produces Newton's force, our test patterns
   dissipate too fast to feel it. Synthesizing with Exp 55/56 (collision
   physics, composite objects) — what makes a pattern *self-cohesive*
   under tick dynamics? This is independent of the gradient question
   and was flagged in the April 17 memory as the real frontier.

The "what moves and how" question stayed unresolved at the end of Exp
132. Exp 133 has not resolved it — but has pinned down which
ontological commitment (strict conservation in finite substrate) was
mathematically incompatible with the goal.

## Key numbers (for memory / future reference)

| Quantity | Value | Phase |
|---|---|---|
| Conservation drift | 0 quanta over 2000+ ticks at any α | 1, 2, 2b, 2c, 2d, 2e, 2f |
| Phase 2 closed-loop slope | −0.012 (r²=0.008) | 2 |
| Phase 2c α=5 slope (anti-gravity) | +0.165 (r²=0.71) at tick 100 | 2c |
| Phase 2d α=0 density slope (with sink) | −0.99 (r²=0.96) | 2d |
| Phase 2d α=1 density slope (with sink) | −0.83 (r²=0.98) | 2d |
| Phase 2e raw gradient slope | −0.10 (r²=0.01) | 2e |
| Phase 2f k=10 smoothed gradient slope | −0.65 (r²=0.50) | 2f |
| Phase 2f k=10 mean cos(θ to star) | +0.48 | 2f |
| Phase 2f k=10 max cos(θ) at r≈0.029 | +0.86 | 2f |
| Phase 3b net drift | −0.0007 over 1500 ticks (noise) | 3b |
| Substrate throughput | ~30 t/s at N=100k single thread | various |
| Tick rule unit tests | 16 passing | — |

## Honest summary

Did we earn substrate orbital mechanics? **No.** Phases 4 and 5 were
not even attempted because Phase 2 falsified the prerequisite (no
sustained field under closed-loop conservation), and the source/sink
revision in Phase 2d, while it produced a real radial gradient, gave
the wrong exponent (−0.65 smoothed force law, not Newton's −2).

Did we learn something? **Yes.** Three concrete things:

1. The strict conservation commitment from RAW 28 / spec §2 is
   mathematically incompatible with sustained radial fields in finite
   substrates. Real physics gets away with it because the universe is
   so much larger than any local experiment that the boundary is
   irrelevant on observation timescales. We can't reproduce that scale.
2. Integer quantization + threshold firing (the spec's hold-and-fire
   capacitor reading of RAW 126) produces a power-law field but with
   the wrong exponent. Pure-real diffusion (128 v11) earned Newton's
   exponent on the same topology. Quantization changes the macroscopic
   physics.
3. Per-cell-scale renewal works; entity-scale renewal doesn't on these
   parameters. Test patterns dissipate before they can move. The Doc 28
   "renewal-not-identity" commitment is correct in spirit but fails
   operationally for entity-scale objects unless the rule supports
   self-coherent patterns. That is the same gap Exp 132 hit.

This is the third weekend in a row that closes with a different
diagnosis of the same broad gap. The pattern is becoming legible:
substrate microdynamics produce *some* macroscale structure, but the
combination of "strict conservation + isotropic + cell-level rule" never
produces the *right* macroscale structure with patterns that persist.
The next experiment should confront one of those three commitments
directly, not stack a fourth rule modification on top of all of them.
