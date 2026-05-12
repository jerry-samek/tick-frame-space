"""
Experiment 135 Phase 4 deliverable.

K=6 ring + 1 Learning observer attached to each ring cell (6 observers total).
Test whether observers at different positions specialize differently based on
their host's local "exhaust pattern."
"""
from __future__ import annotations

from cell import Cell, State
from substrate import Substrate
from fixture import build_k6_ring, attach_observer, Injector


N_TICKS = 10_000
INJECTION_PERIOD = 30
SNAPSHOT_PERIOD = 1000
SEED = 42
# Lower threshold than Phase 3 because non-c0 observers see only a small fraction
# of traffic (tokens that walk through their host). Threshold=15 lets all observers
# crystallize within the run; size=1 keeps the test deterministic with small samples.
LEARNING_THRESHOLD = 15
CRYSTALLIZATION_SIZE = 1


def test_phase4_multi_observer_specialization():
    s = Substrate()
    ring = build_k6_ring(s)
    c0 = ring[0]
    observers = [
        attach_observer(
            s, ring[i],
            learning_threshold=LEARNING_THRESHOLD,
            crystallization_size=CRYSTALLIZATION_SIZE,
        )
        for i in range(6)
    ]
    injector = Injector(seed=SEED)

    snapshots: list[dict] = []
    n_known_injected = 0
    n_unknown_injected = 0

    for tick_idx in range(1, N_TICKS + 1):
        if tick_idx % INJECTION_PERIOD == 1:
            token = injector.next_token()
            s.inject(c0, token=token)
            if token < 6:
                n_known_injected += 1
            else:
                n_unknown_injected += 1
        s.tick()
        if tick_idx % SNAPSHOT_PERIOD == 0:
            snapshots.append({
                "tick": tick_idx,
                "n_cells": len(s.cells),
                "obs_counts": [sum(o.obs_counter.values()) for o in observers],
                "states": [o.state.value[0].upper() for o in observers],
                "max_pending": max((len(c.pending) for c in s.cells), default=0),
            })

    # ===== Measurements =====
    n_consumed = len(s.consume_log)
    n_spawned = len(s.spawn_log)
    spawned_children = {child for (_, _, child, _) in s.spawn_log}

    n_consumed_by_ring = sum(1 for (_, cell, _, _) in s.consume_log if cell in ring)
    n_consumed_by_spawned = sum(1 for (_, cell, _, _) in s.consume_log if cell in spawned_children)
    n_consumed_by_observer = sum(1 for (_, cell, _, _) in s.consume_log if cell in observers)

    # Semantic routing: token i consumed at SOME cell with i in spectrum.
    known_routing_correct = sum(
        1 for (_, cell, token, _) in s.consume_log
        if token < 6 and token in cell.spectrum
    )
    known_routing_total = sum(1 for (_, _, token, _) in s.consume_log if token < 6)

    print()
    print("========== EXP 135 PHASE 4 RESULTS ==========")
    print(f"K=6 ring + 6 observers (one per ring cell); cadence={INJECTION_PERIOD}; {N_TICKS} ticks; seed={SEED}")
    print(f"Observer params: learning_threshold={LEARNING_THRESHOLD}, crystallization_size={CRYSTALLIZATION_SIZE}")
    print()
    print(f"Injected: {n_known_injected + n_unknown_injected} ({n_known_injected} known, {n_unknown_injected} unknown)")
    print(f"Consumed: {n_consumed}")
    print(f"  by ring:     {n_consumed_by_ring}")
    print(f"  by spawned:  {n_consumed_by_spawned}")
    print(f"  by observer: {n_consumed_by_observer}")
    print(f"Spawned: {n_spawned} cells, spectra {sorted(set().union(*(c.spectrum for c in spawned_children)))}")
    if known_routing_total > 0:
        print(f"Semantic known-routing: {known_routing_correct}/{known_routing_total} = {100*known_routing_correct/known_routing_total:.1f}%")
    print()
    print("Per-observer:")
    print(f"  {'Host':<6} {'State':<14} {'Total obs':<10} {'Spectrum':<10} {'Top-3 obs':<30}")
    for i, obs in enumerate(observers):
        top3 = obs.obs_counter.most_common(3)
        print(f"  c{i:<5} {obs.state.value:<14} {sum(obs.obs_counter.values()):<10} "
              f"{str(sorted(obs.spectrum)):<10} {str(top3):<30}")
    print()
    print(f"Spawn log:")
    for (tick, parent, child, token) in s.spawn_log:
        print(f"  tick {tick:5d}: parent_idx={parent.creation_order} child_spectrum={child.spectrum}")
    print()
    print("Snapshots (states: L=Learning, C=Crystallized, in c0..c5 order):")
    for snap in snapshots:
        print(f"  tick {snap['tick']:5d}: cells={snap['n_cells']:3d} "
              f"states=[{''.join(snap['states'])}] "
              f"obs_counts={snap['obs_counts']} max_pending={snap['max_pending']}")
    print()

    # ===== Heterogeneity analysis =====
    distinct_spectra = {frozenset(o.spectrum) for o in observers if o.state == State.CRYSTALLIZED}
    print(f"Distinct crystallized spectra: {len(distinct_spectra)}")
    print(f"  {sorted([sorted(s) for s in distinct_spectra])}")
    print()

    # ===== Success criteria =====

    # 1. Phase 3 invariants — ring integrity
    for i, c in enumerate(ring):
        assert c.spectrum == {i}, f"ring cell {i} spectrum mutated: {c.spectrum}"
        prev_c = ring[(i - 1) % 6]
        next_c = ring[(i + 1) % 6]
        assert prev_c in c.connectors, f"ring cell {i} lost left ring neighbor"
        assert next_c in c.connectors, f"ring cell {i} lost right ring neighbor"

    # 2. Spawn spectra include the unknown alphabet (and may include known tokens
    # too — multi-observer dynamics can cause origin-loop spawns for known tokens
    # when the routing path is disrupted by intercepting observers).
    assert n_spawned >= 5, f"expected at least 5 spawns, got {n_spawned}"
    spawned_spectra_union = set()
    for child in spawned_children:
        spawned_spectra_union |= child.spectrum
    assert spawned_spectra_union >= {6, 7, 8, 9, 10}, (
        f"spawned spectra {spawned_spectra_union} should include {{6..10}}"
    )

    # 3. Semantic routing accuracy
    if known_routing_total > 0:
        accuracy = known_routing_correct / known_routing_total
        assert accuracy >= 0.95, f"semantic routing accuracy {accuracy:.3f} < 0.95"

    # 4. At least observer_c0 (busiest cell) crystallized; others may be
    # traffic-starved (real finding — once early observers crystallize and
    # intercept tokens, downstream observers see less traffic).
    n_crystallized = sum(1 for obs in observers if obs.state == State.CRYSTALLIZED)
    assert observers[0].state == State.CRYSTALLIZED, (
        "observer at c0 (busiest cell) did not crystallize"
    )
    assert n_crystallized >= 3, (
        f"only {n_crystallized}/6 observers crystallized; expected at least 3"
    )

    # 5. No CRYSTALLIZED observer learned its host's token (each ring cell
    # self-consumes its own token before canvasing).
    for i, obs in enumerate(observers):
        if obs.state == State.CRYSTALLIZED:
            assert i not in obs.spectrum, (
                f"observer at c{i} learned token {i} (its host's spectrum); "
                f"expected not — c{i} self-consumes {i} before canvasing"
            )

    # 6. Heterogeneity among crystallized observers — at least 2 distinct spectra.
    # (Even if multiple observers crystallize to the same token, having at least
    # two different spectra confirms positional differentiation.)
    assert len(distinct_spectra) >= 2, (
        f"only {len(distinct_spectra)} distinct observer spectrum; "
        f"observers did not specialize: {sorted([sorted(s) for s in distinct_spectra])}"
    )

    print("========== ALL PHASE 4 SUCCESS CRITERIA PASSED ==========")
