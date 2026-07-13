"""Phase 2 test scenarios: planet + test pattern placements.

Each scenario is a dict with planet_cycle, test_cycle, and a description.
The cycles are lists of (x, y, z) cells in cycle order, ready for
rule.bootstrap().
"""

# Planet is the same in all scenarios: F1 (2x2 square at origin).
PLANET_CYCLE = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]


SCENARIOS = {
    "S1_face_adjacent": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)],
        "description": (
            "Test pattern's (2,0,0) is face-adjacent to planet's (1,0,0). "
            "Planet and test fuse into one 8-cell connected component at "
            "bootstrap. Predicted: contact-ambiguity dissolution."
        ),
    },
    "S2_one_cell_gap": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(3, 0, 0), (4, 0, 0), (4, 1, 0), (3, 1, 0)],
        "description": (
            "1-cell empty gap at (2,0,0) between nearest cells. Patterns are "
            "separate connected components. Positive control for substrate "
            "locality. Predicted: both invariant for 1000 cycles."
        ),
    },
    "S3_two_cell_gap": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(4, 0, 0), (5, 0, 0), (5, 1, 0), (4, 1, 0)],
        "description": (
            "2-cell empty gap. Same predicted behavior as S2; runs as a "
            "second positive control."
        ),
    },
}
