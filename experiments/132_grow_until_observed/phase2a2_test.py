"""Phase 2A.2: load coefficient sweep on planet-only substrate.

Tests whether the substrate-saturation finding from Phase 2A.5 is
parameter-tunable (different load_coefficient values produce different
profiles) or structural (every value gives the same flat profile).

Single-pattern (planet-only) runs at multiple load_coefficient values.
For each, measures threshold(r) and load(r) profiles, monotonicity check.

If ANY value produces a non-flat, monotonic-decreasing profile, we have a
working regime for H3.5/H4.1 — the saturation in Phase 2A.5 was
parameter-bound, not structural.

If NONE do, the substrate's flat-profile is structural to the three-layer
mechanism with full lattice connectivity, and Phase 2A.4 (partial
connectivity) becomes higher priority.

Spec: derived from `2026-04-28-grow-until-observed-phase2a5-design.md` §"Outcome 3 → 2A.2"
"""
from capacitor import Cell, CellState
from lattice import build_connectors, enumerate_cells
from parameters import Parameters
from profile import load_profile, threshold_profile
from recording import Recorder
from tick import build_connector_index, tick


X_RANGE = (0, 21)
Y_RANGE = (0, 21)
Z_RANGE = (0, 3)
PLANET_CYCLE = [(10, 10, 1), (11, 10, 1), (11, 11, 1), (10, 11, 1)]
PLANET_CENTROID = (10.5, 10.5, 1.0)
WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4
SNAPSHOT_INTERVAL = 100

LOAD_SWEEP = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0]


def _bootstrap_pattern(cells, cycle, params):
    for i, pos in enumerate(cycle):
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )


def _setup_planet_only(params):
    all_cells_pos = enumerate_cells(X_RANGE, Y_RANGE, Z_RANGE)
    cells = {}
    for pos in all_cells_pos:
        cells[pos] = Cell(
            charge_level=0.0,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.EMPTY,
        )
    _bootstrap_pattern(cells, PLANET_CYCLE, params)
    connectors = build_connectors(all_cells_pos)
    return cells, connectors


def _run_single(load_coef):
    params = Parameters(
        baseline_threshold=100.0,
        adaptation_rate=0.1,
        relaxation_rate=0.05,
        deposit_amount=50.0,
        load_coefficient=load_coef,
        propagation_time_base=1.0,
        bootstrap_charge_step=0.25,
    )
    cells, connectors = _setup_planet_only(params)
    connector_index = build_connector_index(connectors)
    rec = Recorder()
    current_tick = 0
    total_ticks = (WARMUP_CYCLES + TARGET_CYCLES) * K
    for _ in range(total_ticks):
        current_tick += 1
        tick(cells, connectors, current_tick, params, connector_index)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)
    final = rec.snapshots[-1]
    return final["thresholds"], final["loads"]


def _is_monotonic_decreasing(profile):
    sorted_radii = sorted(profile.keys())
    if len(sorted_radii) < 2:
        return True
    return all(
        profile[a] >= profile[b]
        for a, b in zip(sorted_radii, sorted_radii[1:])
    )


def _profile_range(profile):
    if not profile:
        return None
    values = list(profile.values())
    return max(values) - min(values)


def test_phase2a2_load_sweep():
    """Sweep load_coefficient values; report profile shape for each."""
    print("\n========== PHASE 2A.2: LOAD COEFFICIENT SWEEP ==========")
    print(f"Sweeping load_coefficient over {LOAD_SWEEP}")
    print(f"All other params fixed; planet-only substrate, 5000 cycles each.\n")

    results = []
    for load_coef in LOAD_SWEEP:
        print(f"--- Running load_coefficient = {load_coef} ---")
        thr_state, load_state = _run_single(load_coef)

        thr_profile = threshold_profile(thr_state, center=PLANET_CENTROID)
        load_pr = load_profile(load_state, center=PLANET_CENTROID)

        thr_monotonic = _is_monotonic_decreasing(thr_profile)
        load_monotonic = _is_monotonic_decreasing(load_pr)
        thr_range = _profile_range(thr_profile)
        load_range = _profile_range(load_pr)

        results.append({
            "load_coef": load_coef,
            "thr_profile": thr_profile,
            "load_profile": load_pr,
            "thr_monotonic": thr_monotonic,
            "load_monotonic": load_monotonic,
            "thr_range": thr_range,
            "load_range": load_range,
        })

        print(f"  threshold(r) range (max-min): {thr_range:.4f}")
        print(f"  threshold(r) monotonic decreasing: {thr_monotonic}")
        print(f"  load(r) range (max-min): {load_range:.4f}")
        print(f"  load(r) monotonic decreasing: {load_monotonic}")
        print()

    print("========== SWEEP SUMMARY ==========")
    print(f"{'load_coef':>10} | {'thr_range':>10} | {'thr_mono':>9} | {'load_range':>10} | {'load_mono':>9}")
    print("-" * 70)
    for r in results:
        print(
            f"{r['load_coef']:>10.4f} | "
            f"{r['thr_range']:>10.4f} | "
            f"{str(r['thr_monotonic']):>9} | "
            f"{r['load_range']:>10.4f} | "
            f"{str(r['load_monotonic']):>9}"
        )

    print("\n========== DETAILED PROFILES (all sweep values) ==========")
    for r in results:
        print(f"\n--- load_coefficient = {r['load_coef']} ---")
        print("threshold(r):")
        for radius in sorted(r["thr_profile"].keys())[:12]:
            print(f"  r={radius}: {r['thr_profile'][radius]:.4f}")
        print("load(r):")
        for radius in sorted(r["load_profile"].keys())[:12]:
            print(f"  r={radius}: {r['load_profile'][radius]:.4f}")

    # Identify the most promising load_coefficient (largest threshold range, ideally monotonic)
    best_thr = max(results, key=lambda r: (r["thr_monotonic"], r["thr_range"]))
    print("\n========== INTERPRETATION ==========")
    print(f"Best threshold profile: load_coefficient={best_thr['load_coef']} "
          f"(range={best_thr['thr_range']:.4f}, monotonic={best_thr['thr_monotonic']})")
    any_monotonic = any(r["thr_monotonic"] for r in results) or any(r["load_monotonic"] for r in results)
    if any_monotonic:
        print("AT LEAST ONE sweep value produces monotonic decreasing profile.")
        print("Saturation is PARAMETER-TUNABLE; H3.5/H4.1 may have a working regime.")
    else:
        print("NO sweep value produces a monotonic decreasing profile.")
        print("Saturation appears STRUCTURAL to full lattice connectivity.")
        print("Phase 2A.4 (partial connectivity) becomes higher priority.")
    print("========== END PHASE 2A.2 ==========\n")
