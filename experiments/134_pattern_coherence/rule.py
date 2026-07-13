"""Sign-blind transactional renewal rule (Step A + Step B + tick).

See docs/superpowers/specs/2026-04-28-pattern-coherence-design.md.
"""

from substrate import Canvas, Cell, decay, face_neighbors


def bootstrap(canvas: Canvas, cycle: list[Cell], sign: int = 1) -> None:
    """Seed canvas with cycle cells at gamma = sign * K, sign * (K-1), ..., sign * 1.

    `cycle` is the Hamiltonian cycle in cycle order. `sign` is +1 (matter) or -1 (antimatter).
    """
    if sign not in (1, -1):
        raise ValueError(f"sign must be +1 or -1, got {sign}")
    K = len(cycle)
    for i, cell in enumerate(cycle):
        canvas[cell] = sign * (K - i)


def find_c_max(canvas: Canvas) -> Cell:
    """Return the cell with maximum |gamma|. Raises if canvas is empty."""
    if not canvas:
        raise ValueError("canvas is empty; no max cell")
    return max(canvas.keys(), key=lambda c: abs(canvas[c]))


def find_c_min_positive(canvas: Canvas) -> Cell:
    """Return the cell with minimum |gamma| among cells with gamma != 0.
    Raises if canvas has no nonzero cells.
    """
    nonzero = [c for c in canvas if canvas[c] != 0]
    if not nonzero:
        raise ValueError("canvas has no nonzero cells")
    return min(nonzero, key=lambda c: abs(canvas[c]))


def find_c0(canvas: Canvas, c_max: Cell, c_min: Cell) -> Cell:
    """Return the unique gamma = 0 cell face-adjacent to both c_max and c_min.

    Raises ValueError if no such cell exists (wedged) or if multiple
    such cells exist (non-uniqueness — fixture violates geometric constraint).
    """
    common = set(face_neighbors(c_max)) & set(face_neighbors(c_min))
    candidates = [c for c in common if canvas.get(c, 0) == 0]
    if len(candidates) == 0:
        raise ValueError(
            f"wedged state: no gamma=0 cell face-adjacent to both "
            f"c_max={c_max} and c_min={c_min}"
        )
    if len(candidates) > 1:
        raise ValueError(
            f"non-unique c0 (multiple candidates {candidates}): fixture "
            f"violates geometric constraint that cycle-distance-2 pairs "
            f"have all common face-neighbors as pattern cells"
        )
    return candidates[0]


def step_b(canvas: Canvas) -> None:
    """Apply Step B: paint c0 to magnitude |gamma[c_max]| + 1 with sign matching c_max."""
    c_max = find_c_max(canvas)
    c_min = find_c_min_positive(canvas)
    c0 = find_c0(canvas, c_max, c_min)
    gamma_max = canvas[c_max]
    sign = 1 if gamma_max > 0 else -1
    canvas[c0] = sign * (abs(gamma_max) + 1)


def tick(canvas: Canvas) -> None:
    """One full substrate tick: decay (Step A) then paint (Step B). In-place."""
    decay(canvas)
    step_b(canvas)
