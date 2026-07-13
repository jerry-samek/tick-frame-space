# experiments/132_grow_until_observed/phase2a5_test.py
"""Phase 2A.5 deliverable: three-run superposition test for self-subtracting
transport (RAW 132 §3.5 H5.7).

R1: planet-only run, 5000 cycles
R2: test-only run, 5000 cycles
R3: planet+test combined run, 5000 cycles (same as Phase 2)

Tests whether R3 - R2 ≈ R1 at test-pattern cells.

Spec: docs/superpowers/specs/2026-04-28-grow-until-observed-phase2a5-design.md
"""
from capacitor import Cell, CellState
from lattice import build_connectors, enumerate_cells
from parameters import Parameters
from phase2a5_analysis import (
    entity_relative_profile,
    is_monotonic_decreasing,
    linearity_statistic,
)
from profile import load_profile, threshold_profile
from recording import Recorder
from tick import build_connector_index, tick


# Same parameters as Phase 2 — DO NOT retune.
PARAMS = Parameters(
    baseline_threshold=100.0,
    adaptation_rate=0.1,
    relaxation_rate=0.05,
    deposit_amount=50.0,
    load_coefficient=0.1,
    propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)

X_RANGE = (0, 21)
Y_RANGE = (0, 21)
Z_RANGE = (0, 3)
PLANET_CYCLE = [(10, 10, 1), (11, 10, 1), (11, 11, 1), (10, 11, 1)]
TEST_CYCLE = [(15, 10, 1), (16, 10, 1), (16, 11, 1), (15, 11, 1)]
PLANET_CENTROID = (10.5, 10.5, 1.0)
TEST_CENTROID = (15.5, 10.5, 1.0)
WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4
SNAPSHOT_INTERVAL = 100


def _bootstrap_pattern(cells, cycle, params):
    for i, pos in enumerate(cycle):
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )


def _setup(include_planet: bool, include_test: bool):
    """Build substrate; optionally bootstrap planet, test pattern, or both."""
    all_cells_pos = enumerate_cells(X_RANGE, Y_RANGE, Z_RANGE)
    cells = {}
    for pos in all_cells_pos:
        cells[pos] = Cell(
            charge_level=0.0,
            threshold=PARAMS.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.EMPTY,
        )
    if include_planet:
        _bootstrap_pattern(cells, PLANET_CYCLE, PARAMS)
    if include_test:
        _bootstrap_pattern(cells, TEST_CYCLE, PARAMS)
    connectors = build_connectors(all_cells_pos)
    return cells, connectors


def _run_single(label: str, include_planet: bool, include_test: bool):
    """Run one configuration; return final thresholds dict and final loads dict."""
    cells, connectors = _setup(include_planet, include_test)
    connector_index = build_connector_index(connectors)
    rec = Recorder()
    current_tick = 0
    total_ticks = (WARMUP_CYCLES + TARGET_CYCLES) * K
    for _ in range(total_ticks):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS, connector_index)
        rec.log_firings(current_tick, fired)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)
    final = rec.snapshots[-1]
    print(f"\n  [{label}] completed {current_tick} ticks; final snapshot at tick {final['tick']}")
    return final["thresholds"], final["loads"], rec.firings


def test_phase2a5_superposition():
    """The deliverable: run R1, R2, R3 and report superposition test results."""
    print("\n========== PHASE 2A.5: THREE-RUN SUPERPOSITION TEST ==========")
    print("Running R1 (planet-only)...")
    r1_thr, r1_load, r1_fires = _run_single("R1 planet-only", include_planet=True, include_test=False)

    print("Running R2 (test-only)...")
    r2_thr, r2_load, r2_fires = _run_single("R2 test-only", include_planet=False, include_test=True)

    print("Running R3 (planet+test combined)...")
    r3_thr, r3_load, r3_fires = _run_single("R3 combined", include_planet=True, include_test=True)

    # === Analyses ===
    print("\n----- Linearity statistics -----")
    chi2_thr = linearity_statistic(r1_thr, r2_thr, r3_thr)
    chi2_load = linearity_statistic(r1_load, r2_load, r3_load)
    print(f"chi^2 (thresholds): {chi2_thr:.6f}")
    print(f"chi^2 (loads):      {chi2_load:.6f}")

    # === R1 profile (planet-only profile, the "true" planet signature) ===
    print("\n----- R1 (planet-only) threshold(r) profile from planet centroid -----")
    r1_thr_profile = threshold_profile(r1_thr, center=PLANET_CENTROID)
    for r in sorted(r1_thr_profile.keys())[:12]:
        print(f"  r={r}: threshold = {r1_thr_profile[r]:.4f}")
    r1_thr_monotonic = is_monotonic_decreasing(r1_thr_profile)
    print(f"  R1 threshold(r) monotonically decreasing? {r1_thr_monotonic}")

    print("\n----- R1 (planet-only) load(r) profile from planet centroid -----")
    r1_load_profile = load_profile(r1_load, center=PLANET_CENTROID)
    for r in sorted(r1_load_profile.keys())[:12]:
        print(f"  r={r}: load = {r1_load_profile[r]:.4f}")
    r1_load_monotonic = is_monotonic_decreasing(r1_load_profile)
    print(f"  R1 load(r) monotonically decreasing? {r1_load_monotonic}")

    # === Entity-relative profile: (R3 - R2)(r) from planet centroid ===
    print("\n----- Entity-relative threshold profile (R3-R2)(r) from planet centroid -----")
    er_thr_profile = entity_relative_profile(r3_thr, r2_thr, center=PLANET_CENTROID)
    for r in sorted(er_thr_profile.keys())[:12]:
        print(f"  r={r}: (R3-R2) threshold = {er_thr_profile[r]:.4f}")
    er_thr_monotonic = is_monotonic_decreasing(er_thr_profile)
    print(f"  Entity-relative threshold monotonically decreasing? {er_thr_monotonic}")

    print("\n----- Entity-relative load profile (R3-R2)(r) from planet centroid -----")
    er_load_profile = entity_relative_profile(r3_load, r2_load, center=PLANET_CENTROID)
    for r in sorted(er_load_profile.keys())[:12]:
        print(f"  r={r}: (R3-R2) load = {er_load_profile[r]:.4f}")
    er_load_monotonic = is_monotonic_decreasing(er_load_profile)
    print(f"  Entity-relative load monotonically decreasing? {er_load_monotonic}")

    # === Outcome categorization ===
    print("\n----- OUTCOME CATEGORIZATION -----")
    if chi2_thr < 0.001 and chi2_load < 0.001:
        outcome = "1 (superposition holds tightly)"
    elif chi2_thr < 0.1 and chi2_load < 0.1:
        outcome = "2 (approximate superposition with deviations)"
    else:
        outcome = "3 (superposition fails)"
    print(f"Outcome category: {outcome}")
    print(f"  R1 thresholds monotonic? {r1_thr_monotonic}")
    print(f"  R1 loads monotonic? {r1_load_monotonic}")
    print(f"  Entity-relative threshold monotonic? {er_thr_monotonic}")
    print(f"  Entity-relative load monotonic? {er_load_monotonic}")

    print("\n========== END PHASE 2A.5 ==========")
