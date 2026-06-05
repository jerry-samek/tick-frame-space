#!/usr/bin/env python3
"""R5 ratification (RAW 402): is the Phase 2 'planet field saturation' actually
whole-lattice runaway ignition with no localized planet field?

PRE-REGISTRATION (committed before running):
  Hypothesis H_R5: the 21x21x3 full-connectivity lattice with deposit_amount=50,
  threshold=100 (2 arrivals -> fire), charge non-decaying, undergoes whole-lattice
  ignition, so H3.5/H4.1 were never tested against a localized planet field.

  Observables:
    O1: per-tick fired-cell count over T=400 ticks for 4 configs:
        full (planet+test), planet-only, test-only, empty.
    O2: final threshold(r) profile around PLANET_CENTROID for each config.

  Pre-committed verdicts:
    - SANITY: empty config fires 0 cells at every tick (else the harness is broken).
    - IGNITION CONFIRMED if any seeded config reaches > 50% of 1323 cells (>661)
      firing within 400 ticks.
    - NO-PLANET-FIELD CONFIRMED if planet-only ignites the lattice broadly AND its
      threshold(r) is ~flat (max-min spread < 5% of baseline across r), i.e. no
      localized decaying field around the planet.
    - CLAIM OVERTURNED if planet-only stays quiescent (peak fired-count stays small,
      say < 30) while a localized threshold(r) gradient forms around the planet.
  No tuning, no parameter sweep. One run per config.
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from capacitor import Cell, CellState
from lattice import build_connectors, enumerate_cells
from parameters import Parameters
from tick import build_connector_index, tick

# EXACT Phase 2 params (phase2_test.py).
PARAMS = Parameters(
    baseline_threshold=100.0, adaptation_rate=0.1, relaxation_rate=0.05,
    deposit_amount=50.0, load_coefficient=0.1, propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)
X_RANGE, Y_RANGE, Z_RANGE = (0, 21), (0, 21), (0, 3)
PLANET_CYCLE = [(10, 10, 1), (11, 10, 1), (11, 11, 1), (10, 11, 1)]
PLANET_CENTROID = (10.5, 10.5, 1.0)
TEST_CYCLE = [(15, 10, 1), (16, 10, 1), (16, 11, 1), (15, 11, 1)]
N_CELLS = (X_RANGE[1] - X_RANGE[0]) * (Y_RANGE[1] - Y_RANGE[0]) * (Z_RANGE[1] - Z_RANGE[0])
T = 400


def _bootstrap(cells, cycle):
    for i, pos in enumerate(cycle):
        frac = 1.0 - i * PARAMS.bootstrap_charge_step
        cells[pos] = Cell(charge_level=frac * PARAMS.baseline_threshold,
                          threshold=PARAMS.baseline_threshold,
                          last_discharge_tick=-1, state=CellState.CHARGING)


def _setup(include_planet, include_test):
    allpos = enumerate_cells(X_RANGE, Y_RANGE, Z_RANGE)
    cells = {pos: Cell(charge_level=0.0, threshold=PARAMS.baseline_threshold,
                       last_discharge_tick=-1, state=CellState.EMPTY) for pos in allpos}
    if include_planet:
        _bootstrap(cells, PLANET_CYCLE)
    if include_test:
        _bootstrap(cells, TEST_CYCLE)
    return cells, build_connectors(allpos)


def run(label, include_planet, include_test):
    cells, connectors = _setup(include_planet, include_test)
    idx = build_connector_index(connectors)
    counts = []
    for ct in range(1, T + 1):
        fired = tick(cells, connectors, ct, PARAMS, connector_index=idx)
        counts.append(len(fired))
    # threshold(r) around planet centroid
    buckets = {}
    for pos, c in cells.items():
        d = round(math.dist(pos, PLANET_CENTROID))
        buckets.setdefault(d, []).append(c.threshold)
    profile = {d: sum(v) / len(v) for d, v in sorted(buckets.items())}
    return counts, profile


def summarize(label, counts, profile):
    peak = max(counts)
    final20 = counts[-20:]
    # checkerboard detection: alternating high/low in last 20 ticks
    alt = sum(1 for a, b in zip(final20, final20[1:]) if abs(a - b) > 0.2 * (peak + 1))
    print(f"\n=== {label} ===")
    print(f"  fired/tick: peak={peak} ({100*peak/N_CELLS:.0f}% of {N_CELLS}), "
          f"mean={sum(counts)/len(counts):.1f}, final20={final20}")
    print(f"  first 16 ticks: {counts[:16]}")
    print(f"  alternation events in last 20 ticks: {alt}/19 "
          f"({'checkerboard-like' if alt >= 12 else 'not clearly alternating'})")
    thr_vals = list(profile.values())
    spread = max(thr_vals) - min(thr_vals)
    print(f"  threshold(r) around planet centroid (baseline {PARAMS.baseline_threshold}):")
    for d, t in profile.items():
        if d <= 12:
            print(f"    r={d:>2}: threshold={t:.3f}")
    print(f"  threshold spread (max-min across r) = {spread:.3f} "
          f"({100*spread/PARAMS.baseline_threshold:.2f}% of baseline)")
    return peak, spread


def main():
    print(f"R5 ignition control: {N_CELLS} cells, full connectivity, T={T} ticks, "
          f"deposit={PARAMS.deposit_amount}, threshold={PARAMS.baseline_threshold}")
    results = {}
    for label, p, t in [("FULL (planet+test)", True, True),
                        ("PLANET-ONLY", True, False),
                        ("TEST-ONLY", False, True),
                        ("EMPTY", False, False)]:
        counts, profile = run(label, p, t)
        results[label] = summarize(label, counts, profile)

    print("\n========== R5 VERDICT ==========")
    empty_peak = results["EMPTY"][0]
    print(f"SANITY (empty fires 0): {'PASS' if empty_peak == 0 else 'FAIL peak=' + str(empty_peak)}")
    ign_threshold = 0.5 * N_CELLS
    ignited = {k: v[0] for k, v in results.items() if v[0] > ign_threshold and k != "EMPTY"}
    print(f"IGNITION (>50%={ign_threshold:.0f} cells): "
          f"{', '.join(f'{k}={v}' for k,v in ignited.items()) if ignited else 'none reached 50%'}")
    p_peak, p_spread = results["PLANET-ONLY"]
    if p_peak > ign_threshold and p_spread < 0.05 * PARAMS.baseline_threshold:
        print(f"NO-PLANET-FIELD CONFIRMED: planet-only ignites broadly (peak={p_peak}) "
              f"with flat threshold(r) (spread {p_spread:.3f}). H3.5/H4.1 had no planet field to test.")
    elif p_peak < 30:
        print(f"CLAIM OVERTURNED: planet-only stays quiescent (peak={p_peak}); "
              f"threshold(r) spread {p_spread:.3f} — a localized field, not ignition.")
    else:
        print(f"PARTIAL/INTERMEDIATE: planet-only peak={p_peak}, threshold spread={p_spread:.3f} "
              f"— neither clean whole-lattice ignition nor a quiet localized field. Report as-is.")


if __name__ == "__main__":
    main()
