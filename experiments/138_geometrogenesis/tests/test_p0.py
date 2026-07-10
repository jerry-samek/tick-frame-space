import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from p0_condensation import metropolis_run  # noqa: E402


def test_run_is_deterministic_degree_preserving_trianglefree():
    r1 = metropolis_run(64, 4, coupling=2.0, sweeps=5, seed=7, check_every=5)
    r2 = metropolis_run(64, 4, coupling=2.0, sweeps=5, seed=7, check_every=5)
    assert r1["energy_trace"] == r2["energy_trace"]
    adj = r1["adj"]
    assert all(len(nbrs) == 4 for nbrs in adj)
    # triangle-free maintained by the hard-core constraint
    s = [set(x) for x in adj]
    assert all(not (s[i] & s[j]) for i in range(len(s)) for j in s[i] if i < j)


def test_energy_drift_is_monitored_and_bounded_relative():
    r = metropolis_run(64, 4, coupling=2.0, sweeps=50, seed=3, check_every=25)
    assert len(r["checkpoints"]) >= 3  # sweep 0 + 2 resyncs
    for c in r["checkpoints"][1:]:
        # radius-1-ball delta-H: residual drift must stay small vs energy scale
        assert abs(c["energy_drift"]) <= 0.1 * abs(c["energy_full"]) + 1.0
