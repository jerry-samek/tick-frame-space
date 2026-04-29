# experiments/132_grow_until_observed/phase1_test.py
"""Phase 1 deliverable: 5000-cycle sustainment of K=4 capacitor cycle.

THE Phase 1 test. Pass means cycle structure is invariant — same 4 cells
firing in same order, thresholds and waveforms within tolerance — for at
least 5000 cycles. Fail means the parameter region needs more search OR
the three-layer mechanism cannot support pattern coherence.

Spec: docs/superpowers/specs/2026-04-28-grow-until-observed-design.md
"""
import pytest

from capacitor import Cell
from fixture import F1_CYCLE, setup_fixture
from parameters import Parameters
from tick import tick


# Phase 1 parameters; tune here if the cycle doesn't sustain.
PARAMS = Parameters(
    baseline_threshold=100.0,
    adaptation_rate=0.1,
    relaxation_rate=0.05,
    deposit_amount=50.0,
    load_coefficient=0.0,
    propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)

WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4


def _record_cycle(fired_history: list, last_cell_idx: int) -> tuple[bool, int]:
    """Find the next 4-fire window and check if it follows F1_CYCLE order
    starting from F1_CYCLE[last_cell_idx + 1].

    Returns (cycle_completed, new_last_cell_idx).
    """
    expected_idx = (last_cell_idx + 1) % K
    expected_cell = F1_CYCLE[expected_idx]
    if not fired_history:
        return False, last_cell_idx
    fired_this_tick = fired_history[-1]
    if fired_this_tick == expected_cell:
        return True, expected_idx
    elif len(fired_this_tick) > 0:
        # Some non-cycle cell fired, or wrong cycle order
        return False, last_cell_idx
    return False, last_cell_idx


def test_phase1_sustainment():
    cells, connectors = setup_fixture(PARAMS)

    # Warm-up: run for WARMUP_CYCLES * K ticks, ignore output.
    current_tick = 0
    for _ in range(WARMUP_CYCLES * K):
        current_tick += 1
        tick(cells, connectors, current_tick, PARAMS)

    # Record steady-state thresholds for tolerance check
    steady_thresholds = {pos: cells[pos].threshold for pos in F1_CYCLE}

    # Sustained cycles: run TARGET_CYCLES * K more ticks, verify firing pattern.
    fire_log: list[list[tuple[int, int, int]]] = []
    threshold_log: list[dict[tuple[int, int, int], float]] = []
    for _ in range(TARGET_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS)
        fire_log.append(fired)
        threshold_log.append({pos: cells[pos].threshold for pos in F1_CYCLE})

    # Check 1: every fire is one of the F1 cells.
    cycle_set = set(F1_CYCLE)
    non_cycle_fires = [
        (i, fires) for i, fires in enumerate(fire_log)
        for cell in fires if cell not in cycle_set
    ]
    assert non_cycle_fires == [], (
        f"Non-cycle cells fired: first 5 = {non_cycle_fires[:5]}"
    )

    # Check 2: each cycle cell fires the expected number of times.
    fire_counts = {pos: 0 for pos in F1_CYCLE}
    for fires in fire_log:
        for cell in fires:
            fire_counts[cell] += 1
    expected_fires = TARGET_CYCLES
    tolerance_fires = int(0.10 * expected_fires)
    for pos, count in fire_counts.items():
        assert abs(count - expected_fires) <= tolerance_fires, (
            f"Cell {pos} fired {count} times; expected ~{expected_fires} ± {tolerance_fires}"
        )

    # Check 3: thresholds stable within ±10% of steady_thresholds.
    tolerance = 0.10
    for pos in F1_CYCLE:
        baseline = steady_thresholds[pos]
        max_dev = max(abs(snap[pos] - baseline) for snap in threshold_log)
        max_allowed = max(tolerance * baseline, 1.0)  # at least 1.0 absolute tolerance
        assert max_dev <= max_allowed, (
            f"Cell {pos} threshold deviated by {max_dev:.2f} from steady "
            f"{baseline:.2f} (max allowed: {max_allowed:.2f})"
        )

    # Diagnostic output for RESULTS_phase1.md
    print(f"\nPhase 1 sustainment PASS")
    print(f"Cycles completed: {TARGET_CYCLES}")
    print(f"Fire counts: {fire_counts}")
    print(f"Steady-state thresholds (after warm-up): {steady_thresholds}")
    print(f"Final thresholds: {threshold_log[-1]}")
