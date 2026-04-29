"""Phase 1 deliverable: bit-identity at every K-tick boundary for 10,000 cycles.

THE Phase 1 test. Pass for all four fixture configs (F1+, F1-, F2, F3) means
Phase 1 succeeded. Any fail records which fixture and how (drift/wedge/non-uniqueness).
"""

import hashlib

import pytest

import fixtures as f
import rule as r
import substrate as s


N_CYCLES = 10_000


def _canvas_hash(canvas: s.Canvas) -> str:
    items = sorted(canvas.items())
    return hashlib.sha256(repr(items).encode()).hexdigest()


def _run_fixture_phase1(cycle, sign):
    K = len(cycle)
    canvas: s.Canvas = {}
    r.bootstrap(canvas, cycle, sign=sign)

    for _ in range(K):
        r.tick(canvas)
    reference_hash = _canvas_hash(canvas)
    reference_state = dict(canvas)

    for n in range(1, N_CYCLES + 1):
        for _ in range(K):
            r.tick(canvas)
        h = _canvas_hash(canvas)
        if h != reference_hash:
            diff = {
                cell: (reference_state.get(cell), canvas.get(cell))
                for cell in set(reference_state) | set(canvas)
                if reference_state.get(cell) != canvas.get(cell)
            }
            pytest.fail(
                f"Drift at cycle n={n} (substrate tick {(n + 1) * K}): "
                f"hash {reference_hash[:12]}... -> {h[:12]}...; "
                f"diverging cells: {diff}"
            )
    return reference_hash


def test_F1_K4_square_bit_identity_10000_cycles_positive():
    h = _run_fixture_phase1(f.F1_K4_SQUARE, sign=1)
    print(f"\nF1 K=4 (matter) reference hash: {h}")


def test_F1_K4_square_bit_identity_10000_cycles_negative():
    h = _run_fixture_phase1(f.F1_K4_SQUARE, sign=-1)
    print(f"\nF1 K=4 (antimatter) reference hash: {h}")


def test_F2_K6_perimeter_bit_identity_10000_cycles():
    h = _run_fixture_phase1(f.F2_K6_PERIMETER, sign=1)
    print(f"\nF2 K=6 reference hash: {h}")


def test_F3_K8_ring_bit_identity_10000_cycles():
    h = _run_fixture_phase1(f.F3_K8_RING, sign=1)
    print(f"\nF3 K=8 reference hash: {h}")
