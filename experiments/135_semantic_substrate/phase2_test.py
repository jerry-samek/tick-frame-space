"""
Experiment 135 Phase 2 deliverable.

Five isolated cells (no connectors), each driven by its own biased token stream
via cell.classify(). Verify each crystallizes to its expected top-3 spectrum.

This isolates the v8-style learning primitive from canvas/routing dynamics.
"""
from __future__ import annotations
import random

from cell import Cell, State


SEED = 42
N_OBSERVATIONS = 250  # well above learning_threshold=200, gives RNG slack
LEARNING_THRESHOLD = 200
CRYSTALLIZATION_SIZE = 3

# Five biased streams, each token alphabet is disjoint so cells can't accidentally
# learn each other's tokens. Distribution is [60, 25, 12, 3] — strong separation
# between 3rd-rank token (weight 12) and 4th (weight 3), so RNG variance at
# threshold=200 doesn't flip the top-3 ordering.
CELL_BIASES = [
    {0: 60, 1: 25, 2: 12, 3: 3},      # cell 0 → expects {0, 1, 2}
    {4: 60, 5: 25, 6: 12, 7: 3},      # cell 1 → expects {4, 5, 6}
    {8: 60, 9: 25, 10: 12, 11: 3},    # cell 2 → expects {8, 9, 10}
    {12: 60, 13: 25, 14: 12, 15: 3},  # cell 3 → expects {12, 13, 14}
    {16: 60, 17: 25, 18: 12, 19: 3},  # cell 4 → expects {16, 17, 18}
]
EXPECTED_SPECTRA = [
    {0, 1, 2},
    {4, 5, 6},
    {8, 9, 10},
    {12, 13, 14},
    {16, 17, 18},
]


def biased_stream(rng: random.Random, bias: dict[int, int], n: int) -> list[int]:
    tokens = list(bias.keys())
    weights = list(bias.values())
    return rng.choices(tokens, weights=weights, k=n)


def test_phase2_independent_cells_crystallize_correctly():
    cells = [
        Cell(
            spectrum=set(),
            learning_threshold=LEARNING_THRESHOLD,
            crystallization_size=CRYSTALLIZATION_SIZE,
        )
        for _ in range(5)
    ]
    rng = random.Random(SEED)

    streams = [biased_stream(rng, bias, N_OBSERVATIONS) for bias in CELL_BIASES]

    print()
    print("========== EXP 135 PHASE 2 RESULTS ==========")
    print(f"5 isolated cells, {N_OBSERVATIONS} observations each, "
          f"learning_threshold={LEARNING_THRESHOLD}, "
          f"crystallization_size={CRYSTALLIZATION_SIZE}, seed={SEED}")
    print()

    for i, (cell, stream) in enumerate(zip(cells, streams)):
        for token in stream:
            cell.classify(token)
        most_common = cell.obs_counter.most_common()
        print(f"Cell {i}:")
        print(f"  state:       {cell.state.value}")
        print(f"  spectrum:    {sorted(cell.spectrum)}")
        print(f"  expected:    {sorted(EXPECTED_SPECTRA[i])}")
        print(f"  observed:    {[(t, c) for t, c in most_common]}")
        print()

    # ===== Success criteria =====

    # 1. Every cell crystallized.
    for i, cell in enumerate(cells):
        assert cell.state == State.CRYSTALLIZED, (
            f"cell {i} did not crystallize (state={cell.state.value}, "
            f"observed total={sum(cell.obs_counter.values())})"
        )

    # 2. Spectra match expected top-3.
    for i, (cell, expected) in enumerate(zip(cells, EXPECTED_SPECTRA)):
        assert cell.spectrum == expected, (
            f"cell {i} spectrum {sorted(cell.spectrum)} != expected {sorted(expected)}"
        )

    # 3. Continued observation does not change crystallized spectrum.
    rng2 = random.Random(SEED + 1)
    extra_streams = [biased_stream(rng2, bias, 50) for bias in CELL_BIASES]
    for cell, extra in zip(cells, extra_streams):
        spectrum_before = set(cell.spectrum)
        for token in extra:
            cell.classify(token)
        assert cell.spectrum == spectrum_before, (
            f"crystallized spectrum changed: {spectrum_before} -> {cell.spectrum}"
        )

    print("========== ALL PHASE 2 SUCCESS CRITERIA PASSED ==========")
