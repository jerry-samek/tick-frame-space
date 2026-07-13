"""Phase 2 deliverable: contact physics on multi-pattern substrate.

Runs each scenario (S1, S2, S3), captures three observables (identity,
centroid, cycle invariance) over 1000 cycles, asserts on positive controls
(S2, S3 must be invariant), and records S1's full trajectory.

Spec: docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md
"""

import multipattern as mp
import observation as o
import rule as r
import scenarios as sc
import substrate as s

K = 4
N_CYCLES = 1000


def _setup(planet_cycle, test_cycle):
    """Bootstrap planet and test patterns; return (canvas, pattern_id)."""
    canvas: s.Canvas = {}
    pattern_id: o.PatternIdMap = {}
    r.bootstrap(canvas, planet_cycle, sign=1)
    for cell in planet_cycle:
        pattern_id[cell] = "planet"
    r.bootstrap(canvas, test_cycle, sign=1)
    for cell in test_cycle:
        pattern_id[cell] = "test"
    return canvas, pattern_id


def _run_scenario(name: str) -> dict:
    """Run a scenario for N_CYCLES cycles, capturing all three observables."""
    sc_def = sc.SCENARIOS[name]
    canvas, pattern_id = _setup(sc_def["planet_cycle"], sc_def["test_cycle"])

    initial_centroid = o.centroid_alive_tagged(canvas, pattern_id, "test")
    cycle_hashes: list[str] = []
    identity_trajectory: list[tuple[int, int]] = []
    centroid_trajectory: list[tuple[int, tuple[float, float, float] | None]] = []

    for cycle_n in range(1, N_CYCLES + 1):
        for _ in range(K):
            mp.tick_multi(canvas)
        cycle_hashes.append(o.canvas_hash(canvas))
        identity_trajectory.append(
            (cycle_n, o.count_alive_tagged(canvas, pattern_id, "test"))
        )
        centroid_trajectory.append(
            (cycle_n, o.centroid_alive_tagged(canvas, pattern_id, "test"))
        )

    reference_hash = cycle_hashes[0]
    first_break = None
    for i, h in enumerate(cycle_hashes, start=1):
        if h != reference_hash:
            first_break = i
            break

    final_n_alive = identity_trajectory[-1][1]
    final_centroid = centroid_trajectory[-1][1]
    drift = None
    if final_centroid is not None and initial_centroid is not None:
        drift = tuple(final_centroid[i] - initial_centroid[i] for i in range(3))

    return {
        "name": name,
        "description": sc_def["description"],
        "n_cycles_run": N_CYCLES,
        "reference_hash": reference_hash,
        "first_break": first_break,
        "initial_centroid": initial_centroid,
        "final_centroid": final_centroid,
        "drift_vector": drift,
        "final_n_test_alive": final_n_alive,
        "identity_trajectory": identity_trajectory,
        "centroid_trajectory": centroid_trajectory,
    }


def test_S1_face_adjacent_records_contact_event():
    """S1: face-adjacent patterns. We do not predict the exact outcome,
    we record it. The test passes by virtue of completing the run; the
    output (printed for the record) is what RESULTS_phase2.md captures."""
    result = _run_scenario("S1_face_adjacent")
    print(f"\nS1 final n_test_alive: {result['final_n_test_alive']}")
    print(f"S1 first_break: {result['first_break']}")
    print(f"S1 initial centroid: {result['initial_centroid']}")
    print(f"S1 final centroid: {result['final_centroid']}")
    print(f"S1 drift vector: {result['drift_vector']}")
    print(f"S1 identity (first 10 cycles): {result['identity_trajectory'][:10]}")
    print(f"S1 reference hash: {result['reference_hash']}")
    # No assertions — S1 is observational. The print output is the record.


def test_S2_one_cell_gap_is_invariant():
    """S2: 1-cell gap. Positive control. Predicted: invariant for all 1000 cycles,
    centroid stationary, all 4 test cells alive throughout."""
    result = _run_scenario("S2_one_cell_gap")
    print(f"\nS2 reference hash: {result['reference_hash']}")

    assert result["first_break"] is None, (
        f"S2 (positive control) violated invariance at cycle {result['first_break']}: "
        f"the rule has unexpected coupling across a 1-cell gap"
    )
    assert result["final_n_test_alive"] == 4, (
        f"S2 lost {4 - result['final_n_test_alive']} test cells; expected all 4 alive"
    )
    assert result["drift_vector"] == (0.0, 0.0, 0.0), (
        f"S2 centroid drifted by {result['drift_vector']}; expected stationary"
    )


def test_S3_two_cell_gap_is_invariant():
    """S3: 2-cell gap. Second positive control. Same predictions as S2."""
    result = _run_scenario("S3_two_cell_gap")
    print(f"\nS3 reference hash: {result['reference_hash']}")

    assert result["first_break"] is None, (
        f"S3 violated invariance at cycle {result['first_break']}"
    )
    assert result["final_n_test_alive"] == 4
    assert result["drift_vector"] == (0.0, 0.0, 0.0)
