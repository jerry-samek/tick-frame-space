# experiments/132_grow_until_observed/phase2_test.py
"""Phase 2 deliverable: full instrumented run on capacitor substrate with
planet + test patterns + full lattice connectivity, then post-hoc applies
4 reading functions and computes threshold(r) + load(r) profiles.

Tests 4 hypothesis sets per RAW 132 §3.6:
  H3.5 — adaptive threshold profile
  H4.1 — load profile
  H5.1 — primary reading function (drift toward planet)
  H5.3, H5.4, H5.5 — alternative readings (panel comparison)

Spec: docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md
"""
from capacitor import Cell, CellState
from lattice import build_connectors, enumerate_cells
from observer import (
    centroid_connected_firing,
    centroid_recent,
    centroid_threshold_elevated,
    peak_density_map,
)
from parameters import Parameters
from profile import load_profile, threshold_profile
from recording import Recorder
from tick import build_connector_index, tick


# Phase 2 PARAMS. Same as Phase 1 PASS (deposit=50, adapt=0.1, relax=0.05),
# but load_coefficient is now > 0 to exercise the connector layer.
PARAMS = Parameters(
    baseline_threshold=100.0,
    adaptation_rate=0.1,
    relaxation_rate=0.05,
    deposit_amount=50.0,
    load_coefficient=0.1,    # turned on; tune if cycles destabilize
    propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)

# Substrate: 21x21x3 region centered around origin.
X_RANGE = (0, 21)
Y_RANGE = (0, 21)
Z_RANGE = (0, 3)

# Planet at center plane, K=4 cycle.
PLANET_CYCLE = [
    (10, 10, 1),
    (11, 10, 1),
    (11, 11, 1),
    (10, 11, 1),
]
PLANET_CENTROID = (10.5, 10.5, 1.0)

# Test pattern at +5 cells in x.
TEST_CYCLE = [
    (15, 10, 1),
    (16, 10, 1),
    (16, 11, 1),
    (15, 11, 1),
]
TEST_CENTROID = (15.5, 10.5, 1.0)

WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4
SNAPSHOT_INTERVAL = 100  # ticks between substrate snapshots


def _bootstrap_pattern(
    cells: dict, cycle: list, params: Parameters
) -> None:
    """Bootstrap a K=4 pattern with staggered initial charges (matches Phase 1 fixture)."""
    for i, pos in enumerate(cycle):
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )


def _setup() -> tuple[dict, list]:
    """Set up the bounded lattice, full connectors, and bootstrapped patterns."""
    all_cells_pos = enumerate_cells(X_RANGE, Y_RANGE, Z_RANGE)
    cells: dict = {}
    # Initialize all substrate cells with default Cell (charge=0, threshold=baseline, EMPTY)
    for pos in all_cells_pos:
        cells[pos] = Cell(
            charge_level=0.0,
            threshold=PARAMS.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.EMPTY,
        )
    # Bootstrap patterns (overrides defaults at pattern cells)
    _bootstrap_pattern(cells, PLANET_CYCLE, PARAMS)
    _bootstrap_pattern(cells, TEST_CYCLE, PARAMS)
    # Full lattice connectivity
    connectors = build_connectors(all_cells_pos)
    return cells, connectors


def test_phase2_run_and_analyze():
    """Phase 2 deliverable: run, record, post-hoc analyze, report per-hypothesis."""
    cells, connectors = _setup()
    # Build the cell -> connectors index once; reuse across every tick.
    connector_index = build_connector_index(connectors)
    rec = Recorder()

    # Run warmup + target cycles
    current_tick = 0
    for _ in range(WARMUP_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS, connector_index=connector_index)
        rec.log_firings(current_tick, fired)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)

    for _ in range(TARGET_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS, connector_index=connector_index)
        rec.log_firings(current_tick, fired)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)

    # ===== Post-hoc analysis =====

    # H3.5: threshold(r) profile from final snapshot
    final_snapshot = rec.snapshots[-1]
    h35_profile = threshold_profile(final_snapshot["thresholds"], center=PLANET_CENTROID)

    # H4.1: load(r) profile from final snapshot
    h41_profile = load_profile(final_snapshot["loads"], center=PLANET_CENTROID)

    # H5.x: reading functions applied to test pattern's neighborhood, evaluated
    # at every K-tick boundary. We track reading positions over time.
    h51_trajectory = []  # centroid_recent
    h53_trajectory = []  # centroid_threshold_elevated (uses snapshots)
    h54_trajectory = []  # peak_density_map
    h55_trajectory = []  # centroid_connected_firing

    # For H5.x readings, focus on the local neighborhood of the test pattern.
    # We define test-neighborhood as: cells within Manhattan distance 3 of TEST_CENTROID.
    def _is_in_test_neighborhood(pos):
        return abs(pos[0] - TEST_CENTROID[0]) <= 3 and \
               abs(pos[1] - TEST_CENTROID[1]) <= 3 and \
               abs(pos[2] - TEST_CENTROID[2]) <= 1

    # Filter firings to test neighborhood (firings list is ordered)
    test_firings = [(t, c) for t, c in rec.firings if _is_in_test_neighborhood(c)]

    # Sample at every K-tick boundary, starting after warmup
    boundary_start = WARMUP_CYCLES * K
    boundary_end = boundary_start + TARGET_CYCLES * K
    for boundary_tick in range(boundary_start + K, boundary_end + 1, K):
        # H5.1: centroid of cells fired in last K=4 ticks
        h51 = centroid_recent(test_firings, current_tick=boundary_tick, window=K)
        h51_trajectory.append((boundary_tick, h51))

        # H5.4: peak density map (window K, sigma 1.0)
        h54 = peak_density_map(test_firings, current_tick=boundary_tick, window=K, sigma=1.0)
        h54_trajectory.append((boundary_tick, h54))

        # H5.5: centroid of largest connected component
        h55 = centroid_connected_firing(test_firings, current_tick=boundary_tick, window=K)
        h55_trajectory.append((boundary_tick, h55))

    # H5.3 uses snapshots instead of firing log
    for snap in rec.snapshots[WARMUP_CYCLES // (SNAPSHOT_INTERVAL // K) :]:
        # Filter thresholds to test neighborhood
        local_thresholds = {p: t for p, t in snap["thresholds"].items()
                            if _is_in_test_neighborhood(p)}
        h53 = centroid_threshold_elevated(
            local_thresholds, baseline=PARAMS.baseline_threshold, elevation_threshold=0.05
        )
        h53_trajectory.append((snap["tick"], h53))

    # ===== Per-hypothesis report =====

    print("\n========== PHASE 2 RESULTS ==========\n")

    # H3.5
    print("H3.5 — threshold(r) profile (averaged from cells at integer distance from planet):")
    sorted_radii = sorted(h35_profile.keys())
    for r in sorted_radii[:12]:
        print(f"  r={r}: threshold = {h35_profile[r]:.4f}")
    is_decreasing = all(
        h35_profile[r] >= h35_profile[rs]
        for r, rs in zip(sorted_radii, sorted_radii[1:])
        if r in h35_profile and rs in h35_profile
    )
    print(f"  Monotonically decreasing? {is_decreasing}")

    # H4.1
    print("\nH4.1 — load(r) profile (averaged from connectors at integer distance from planet):")
    sorted_radii_load = sorted(h41_profile.keys())
    for r in sorted_radii_load[:12]:
        print(f"  r={r}: load = {h41_profile[r]:.4f}")
    is_decreasing_load = all(
        h41_profile[r] >= h41_profile[rs]
        for r, rs in zip(sorted_radii_load, sorted_radii_load[1:])
        if r in h41_profile and rs in h41_profile
    )
    print(f"  Monotonically decreasing? {is_decreasing_load}")

    # H5.1 trajectory
    print("\nH5.1 — test pattern centroid_recent trajectory (first/last 3 entries):")
    for entry in h51_trajectory[:3]:
        print(f"  tick={entry[0]}, centroid={entry[1]}")
    print("  ...")
    for entry in h51_trajectory[-3:]:
        print(f"  tick={entry[0]}, centroid={entry[1]}")
    initial_x = h51_trajectory[0][1][0] if h51_trajectory[0][1] else None
    final_x = h51_trajectory[-1][1][0] if h51_trajectory[-1][1] else None
    if initial_x is not None and final_x is not None:
        drift_x = final_x - initial_x
        print(f"  Drift in x: {drift_x:.4f} (negative = toward planet at x=10.5)")
    else:
        print(f"  Drift undefined (test pattern not visible in last window)")

    # H5.3, H5.4, H5.5 — show final positions
    print("\nH5.3 — final centroid_threshold_elevated:")
    print(f"  {h53_trajectory[-1] if h53_trajectory else 'no data'}")
    print("\nH5.4 — final peak_density_map:")
    print(f"  {h54_trajectory[-1] if h54_trajectory else 'no data'}")
    print("\nH5.5 — final centroid_connected_firing:")
    print(f"  {h55_trajectory[-1] if h55_trajectory else 'no data'}")

    print("\n========== END RESULTS ==========\n")

    # No assertions — Phase 2 is observational. The print output is the data
    # for RESULTS_phase2.md. Per-hypothesis interpretation done in the writeup.
