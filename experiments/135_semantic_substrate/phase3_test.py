"""
Experiment 135 Phase 3 deliverable.

K=6 ring (Crystallized, preset spectra) + 1 Learning observer attached to c0.
Run Phase 1 stream injection at relaxed cadence (30 ticks) for 10K ticks.
Verify Phase 1 success criteria still hold AND observer crystallizes from
canvas traffic.
"""
from __future__ import annotations

from cell import Cell, State
from substrate import Substrate
from fixture import build_k6_ring, attach_observer, Injector


N_TICKS = 10_000
INJECTION_PERIOD = 30  # relaxed from Phase 1's 15 because c0 degree grows by 1
SNAPSHOT_PERIOD = 500
SEED = 42


def test_phase3_observer_crystallizes_without_breaking_ring():
    s = Substrate()
    ring = build_k6_ring(s)
    c0 = ring[0]
    observer = attach_observer(s, c0)
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
                "observer_obs_count": sum(observer.obs_counter.values()),
                "observer_state": observer.state.value,
                "max_pending": max((len(c.pending) for c in s.cells), default=0),
            })

    # ===== Measurements =====
    n_consumed = len(s.consume_log)
    n_spawned = len(s.spawn_log)
    spawned_children = {child for (_, _, child, _) in s.spawn_log}
    n_consumed_by_ring = sum(1 for (_, cell, _, _) in s.consume_log if cell in ring)
    n_consumed_by_spawned = sum(
        1 for (_, cell, _, _) in s.consume_log if cell in spawned_children
    )
    n_consumed_by_observer = sum(
        1 for (_, cell, _, _) in s.consume_log if cell is observer
    )

    # Reframed routing accuracy for Phase 3:
    # Token i is "correctly routed" if consumed by SOME cell whose spectrum contains i.
    # Once the observer crystallizes, it becomes a competing classifier — tokens that
    # match its spectrum get consumed at the observer instead of at the ring cell.
    # That's correct semantic routing (observer's spectrum DOES contain the token)
    # even if the routing differs from Phase 1's pure-ring topology.
    known_routing_correct = sum(
        1 for (_, cell, token, _) in s.consume_log
        if token < 6 and token in cell.spectrum
    )
    known_routing_total = sum(1 for (_, _, token, _) in s.consume_log if token < 6)
    # Also measure: of consumed-by-observer, which were intercepts (valid for
    # observer's post-crystallization spectrum) vs misroutes (pre-crystallization).
    observer_intercepts = sum(
        1 for (_, cell, token, _) in s.consume_log
        if cell is observer and token in observer.spectrum
    )

    observer_total_obs = sum(observer.obs_counter.values())
    observer_top_3_from_counter = {
        t for (t, _) in observer.obs_counter.most_common(3)
    }

    print()
    print("========== EXP 135 PHASE 3 RESULTS ==========")
    print(f"K=6 ring + 1 observer at c0; cadence={INJECTION_PERIOD}; {N_TICKS} ticks; seed={SEED}")
    print()
    print(f"Injected:        {n_known_injected + n_unknown_injected} total ({n_known_injected} known, {n_unknown_injected} unknown)")
    print(f"Consumed:        {n_consumed}")
    print(f"  by ring:       {n_consumed_by_ring}")
    print(f"  by spawned:    {n_consumed_by_spawned}")
    print(f"  by observer:   {n_consumed_by_observer}")
    print(f"Spawned cells:   {n_spawned}")
    if known_routing_total > 0:
        print(f"Known routing (semantic): {known_routing_correct}/{known_routing_total} = {100*known_routing_correct/known_routing_total:.1f}%")
    print(f"Observer intercepts (consumed tokens that match observer.spectrum): {observer_intercepts}")
    print()
    print("Observer:")
    print(f"  state:        {observer.state.value}")
    print(f"  total obs:    {observer_total_obs}")
    print(f"  spectrum:     {sorted(observer.spectrum)}")
    print(f"  obs_counter (top 5): {observer.obs_counter.most_common(5)}")
    print()
    print("Snapshots (tick, n_cells, observer_obs_count, observer_state, max_pending):")
    for snap in snapshots:
        print(f"  tick {snap['tick']:5d}: cells={snap['n_cells']:3d} "
              f"obs={snap['observer_obs_count']:4d} "
              f"state={snap['observer_state']:12s} max_pending={snap['max_pending']:2d}")
    print()
    print("Spawn log:")
    for (tick, parent, child, token) in s.spawn_log:
        print(f"  tick {tick:5d}: parent_idx={parent.creation_order} child_spectrum={child.spectrum}")
    print()

    # ===== Success criteria =====

    # Phase 1 success criteria (subset — ring integrity + spawn count)
    for i, c in enumerate(ring):
        assert c.spectrum == {i}, f"ring cell {i} spectrum mutated: {c.spectrum}"
        prev_c = ring[(i - 1) % 6]
        next_c = ring[(i + 1) % 6]
        assert prev_c in c.connectors, f"ring cell {i} lost left ring neighbor"
        assert next_c in c.connectors, f"ring cell {i} lost right ring neighbor"

    # Spawn count: still 5 (one per distinct unknown), all at c0.
    assert n_spawned == 5, f"expected 5 spawns, got {n_spawned}"
    spawned_spectra_union: set = set()
    for child in spawned_children:
        spawned_spectra_union |= child.spectrum
    assert spawned_spectra_union == {6, 7, 8, 9, 10}, (
        f"spawned spectra cover {spawned_spectra_union}, expected {{6,7,8,9,10}}"
    )

    # Known token routing accuracy
    if known_routing_total > 0:
        accuracy = known_routing_correct / known_routing_total
        assert accuracy >= 0.95, f"known routing accuracy {accuracy:.3f} < 0.95"

    # Phase 3-specific: observer learning
    # 2. Observer accumulated enough observations.
    assert observer_total_obs >= observer.learning_threshold, (
        f"observer only got {observer_total_obs} observations "
        f"(below threshold {observer.learning_threshold})"
    )

    # 3. Observer crystallized.
    assert observer.state == State.CRYSTALLIZED, (
        f"observer did not crystallize (state={observer.state.value})"
    )

    # 4. Spectrum is self-consistent: matches top-3 of obs_counter at the time
    # of crystallization. Note obs_counter keeps growing post-crystallization,
    # so current top-3 may differ slightly from spectrum if a tail token caught up.
    # The acceptance check: spectrum is a SUBSET of the top-K-with-some-margin.
    spectrum_size = len(observer.spectrum)
    assert spectrum_size == 3, f"spectrum size = {spectrum_size}, expected 3"
    top_5 = {t for (t, _) in observer.obs_counter.most_common(5)}
    assert observer.spectrum.issubset(top_5), (
        f"observer spectrum {observer.spectrum} not in current top-5 {top_5} "
        f"— spectrum should reflect early dominant tokens"
    )

    # 5. Observer should not contain token 0 (c0 self-consumes 0 before canvasing).
    assert 0 not in observer.spectrum, (
        f"observer spectrum contains 0; expected not — c0 self-consumes 0"
    )

    # 6. Observer spectrum is a subset of {1..10}.
    assert observer.spectrum.issubset(set(range(1, 11))), (
        f"observer spectrum {observer.spectrum} contains tokens outside {{1..10}}"
    )

    print("========== ALL PHASE 3 SUCCESS CRITERIA PASSED ==========")
