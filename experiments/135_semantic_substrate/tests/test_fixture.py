from cell import Cell, Response
from substrate import Substrate
from fixture import build_k6_ring, Injector


def test_k6_ring_has_six_cells_with_singleton_spectra():
    s = Substrate()
    cells = build_k6_ring(s)
    assert len(cells) == 6
    for i, c in enumerate(cells):
        assert c.spectrum == {i}


def test_k6_ring_topology_each_cell_linked_to_two_neighbors():
    s = Substrate()
    cells = build_k6_ring(s)
    for i, c in enumerate(cells):
        prev = cells[(i - 1) % 6]
        next_ = cells[(i + 1) % 6]
        assert prev in c.connectors
        assert next_ in c.connectors
        assert len(c.connectors) == 2


def test_k6_ring_classify_responses():
    s = Substrate()
    cells = build_k6_ring(s)
    assert cells[0].classify(0) == Response.SAME
    assert cells[0].classify(3) == Response.DIFFERENT
    assert cells[3].classify(3) == Response.SAME


def test_injector_50_50_mix_with_seeded_rng_is_reproducible():
    inj_a = Injector(seed=42)
    inj_b = Injector(seed=42)
    tokens_a = [inj_a.next_token() for _ in range(100)]
    tokens_b = [inj_b.next_token() for _ in range(100)]
    assert tokens_a == tokens_b


def test_injector_only_emits_from_alphabets():
    inj = Injector(seed=42)
    valid = set(range(6)) | {6, 7, 8, 9, 10}
    for _ in range(1000):
        t = inj.next_token()
        assert t in valid


def test_injector_mix_ratio_approximately_50_50():
    inj = Injector(seed=42)
    known_count = 0
    n = 10000
    for _ in range(n):
        t = inj.next_token()
        if t < 6:
            known_count += 1
    ratio = known_count / n
    assert 0.45 < ratio < 0.55
