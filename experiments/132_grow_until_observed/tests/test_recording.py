# experiments/132_grow_until_observed/tests/test_recording.py
from capacitor import Cell
from connectors import Connector
from recording import Recorder


def test_recorder_logs_firings():
    rec = Recorder()
    rec.log_firings(tick=1, fired=[(0, 0, 0), (1, 0, 0)])
    rec.log_firings(tick=2, fired=[])
    rec.log_firings(tick=3, fired=[(1, 1, 0)])
    assert rec.firings == [
        (1, (0, 0, 0)),
        (1, (1, 0, 0)),
        (3, (1, 1, 0)),
    ]


def test_recorder_snapshot_captures_thresholds_and_loads():
    cells = {
        (0, 0, 0): Cell(charge_level=50.0, threshold=100.5),
        (1, 0, 0): Cell(charge_level=30.0, threshold=100.0),
    }
    connectors = [
        Connector(a=(0, 0, 0), b=(1, 0, 0)),
    ]
    # Simulate one deposit in transit on this connector
    from connectors import Deposit
    connectors[0].in_transit.append(Deposit(remaining_propagation_time=0.5, destination=(1, 0, 0)))

    rec = Recorder()
    rec.snapshot(tick=10, cells=cells, connectors=connectors)
    assert len(rec.snapshots) == 1
    snap = rec.snapshots[0]
    assert snap["tick"] == 10
    assert snap["thresholds"] == {(0, 0, 0): 100.5, (1, 0, 0): 100.0}
    assert snap["loads"] == {((0, 0, 0), (1, 0, 0)): 1}


def test_recorder_skips_empty_firings():
    rec = Recorder()
    rec.log_firings(tick=1, fired=[])
    assert rec.firings == []
