import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from p1_growth import grow  # noqa: E402

BASE = dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True)


def test_growth_is_deterministic_and_past_immutable():
    r1 = grow(dict(BASE), seed=3, max_births=800)
    r2 = grow(dict(BASE), seed=3, max_births=800)
    assert r1["alive_trajectory"] == r2["alive_trajectory"]
    assert r1["deaths"] == r2["deaths"]
    assert r1["record_size"] >= r1["n_alive"]  # dead retained in record


def test_no_decay_control_never_kills():
    p = dict(BASE, decay=False)
    r = grow(p, seed=3, max_births=800)
    assert r["deaths"] == 0
    assert r["n_alive"] == r["record_size"]


def test_any_cycle_control_restores_birth_guarantee():
    # the invalidated P1 rule: any short cycle counts -> survival guaranteed
    # at birth (p=2 parents within distance 2 close a cycle <= 4 = L)
    p = dict(BASE, any_cycle=True)
    r = grow(p, seed=3, max_births=800)
    assert r["deaths"] == 0


def test_reconvergence_selection_actually_kills():
    r = grow(dict(BASE), seed=3, max_births=2000)
    assert r["deaths"] > 0  # the redesigned selector engages
