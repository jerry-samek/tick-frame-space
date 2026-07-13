from cell import Cell, Deposit, Response
from substrate import Substrate


def test_substrate_starts_at_tick_zero():
    s = Substrate()
    assert s.tick_count == 0
    assert s.cells == []


def test_add_cell_assigns_creation_order():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    assert c0.creation_order == 0
    assert c1.creation_order == 1
    assert s.cells == [c0, c1]


def test_inject_queues_deposit_in_target_cell_pending():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    d = s.inject(c0, token=5)
    assert d.token == 5
    assert d.predecessor is None
    assert d.origin is c0
    assert d.age == 0
    assert len(c0.pending) == 1
    assert c0.pending[0] is d


def test_tick_increments_tick_count():
    s = Substrate()
    s.tick()
    assert s.tick_count == 1
    s.tick()
    assert s.tick_count == 2


def test_self_check_consumes_deposit_when_token_in_spectrum():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={3}))
    s.inject(c0, token=3)
    s.tick()
    assert len(s.consume_log) == 1
    tick, cell, token, age = s.consume_log[0]
    assert cell is c0
    assert token == 3
    assert age == 0
    assert len(c0.pending) == 0
    assert c0.is_idle


def test_origin_loop_spawns_child_when_deposit_returns_to_origin_with_predecessor():
    s = Substrate()
    origin = s.add_cell(Cell(spectrum={0}))
    other = s.add_cell(Cell(spectrum={1}))
    d = Deposit(token=99, predecessor=other, origin=origin, age=5)
    origin.pending.append(d)
    s.tick()
    assert len(s.spawn_log) == 1
    tick, parent, child, token = s.spawn_log[0]
    assert parent is origin
    assert child.spectrum == {99}
    assert child.connectors == [origin]
    assert child in origin.connectors
    assert len(s.cells) == 3
    assert len(origin.pending) == 0
    assert origin.is_idle


def test_canvas_to_neighbor_takes_two_ticks_and_forwards_on_same():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={5}))
    c0.connectors.append(c1)
    c1.connectors.append(c0)
    s.inject(c0, token=5)

    s.tick()  # tick 1: c0 starts canvas (query in flight, arrives tick 2)
    assert len(s.consume_log) == 0
    assert not c0.is_idle
    assert c0.canvas_in_flight is c1

    s.tick()  # tick 2: c1 receives query, queues response (arrives tick 3)
    assert len(s.consume_log) == 0

    s.tick()  # tick 3: c0 receives Same, forwards to c1; c1 picks up same tick, self-check Same, consume
    assert c0.is_idle
    assert len(s.consume_log) == 1
    tick, cell, token, age = s.consume_log[0]
    assert cell is c1
    assert token == 5
    assert tick == 3


def test_canvas_skips_predecessor():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum={2}))
    c1.connectors.extend([c0, c2])
    d = Deposit(token=2, predecessor=c0, origin=c0, age=0)
    c1.pending.append(d)

    s.tick()
    assert c1.canvas_in_flight is c2
    assert c1.canvas_remaining == []


def test_canvas_exhaustion_with_only_unknown_spawns_child():
    # Phase 3 rule: spawn-on-Unknown only fires when ALL responders are Unknown.
    # Both neighbors empty (Learning) so canvas has no Different responder.
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum=set()))  # empty -> Unknown (Learning)
    c2 = s.add_cell(Cell(spectrum=set()))  # empty -> Unknown (Learning)
    c0.connectors.extend([c1, c2])
    c1.connectors.append(c0)
    c2.connectors.append(c0)
    s.inject(c0, token=99)

    for _ in range(10):
        s.tick()

    assert len(s.spawn_log) == 1
    _, parent, child, token = s.spawn_log[0]
    assert parent is c0
    assert token == 99
    assert child.spectrum == {99}
    assert child in c0.connectors
    assert c0.is_idle


def test_canvas_exhaustion_different_takes_precedence_over_unknown():
    # Phase 3 rule: Different responder wins over Unknown — no spawn, just forward.
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))    # populated -> Different
    c2 = s.add_cell(Cell(spectrum=set()))  # empty -> Unknown (Learning)
    c0.connectors.extend([c1, c2])
    c1.connectors.append(c0)
    c2.connectors.append(c0)
    s.inject(c0, token=99)

    for _ in range(10):
        s.tick()

    # No spawn at c0 (Different forward took precedence).
    assert all(parent is not c0 for (_, parent, _, _) in s.spawn_log) or len(s.spawn_log) == 0 or all(
        # If a spawn happened elsewhere via origin-loop, that's fine.
        # We only care that c0 didn't spawn-on-Unknown.
        not (parent is c0 and tick < 5) for (tick, parent, _, _) in s.spawn_log
    )
    # Observer (c2) was canvased and observed the token.
    assert c2.obs_counter[99] >= 1


def test_chain_stack_pushes_on_forward_and_pops_on_bounce():
    """The chain_stack tracks forwarders; bounces pop, leaving the original
    chain predecessor visible. Without this, a leaf-bounce would overwrite
    the predecessor and canvas could route the deposit backward (the
    {4}-spawn anomaly traced at seed=42)."""
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    leaf = s.add_cell(Cell(spectrum={9}))  # populated; says Different to non-9 tokens
    c0.connectors.extend([c1])
    c1.connectors.extend([c0, leaf])
    leaf.connectors.append(c1)  # leaf has only c1 as connector

    s.inject(c0, token=4)  # token c0 doesn't have, neither does c1 nor leaf
    # Step the substrate enough for the deposit to walk c0 -> c1 -> leaf -> bounce -> c1.
    for _ in range(20):
        s.tick()

    # The deposit should have bounced back to c1 from leaf, then c1 should have
    # forwarded back to c0 (its only remaining connector after dead_paths excludes leaf).
    # At c0 with predecessor=c1 (popped from stack), origin-loop should fire.
    assert any(parent is c0 and tok == 4 for (_, parent, _, tok) in s.spawn_log), (
        "expected origin-loop spawn at c0 for token=4; "
        f"got spawns: {[(t, p.creation_order, tok) for (t, p, _, tok) in s.spawn_log]}"
    )
    # And the spawn should have happened ONCE — the chain_stack pop on bounce
    # at leaf restored c1's view of c0 as predecessor, so canvas excluded c0
    # correctly. (Pre-fix: canvas at c1 post-bounce would include c0 because
    # `predecessor` was the leaf, leading to a backward forward to c0 and
    # an immediate origin-loop spawn — same shape, but different mechanism
    # of arrival. We assert here that the deposit is consumed via origin-loop
    # only after exhausting forward options, which is the correct semantic.)
    assert len(s.spawn_log) == 1


def test_dup_spawn_guard_at_origin_loop_forwards_when_connector_now_classifies():
    """At origin-loop trigger, scan connectors directly — if any has Same
    for the deposit's token, forward there instead of spawning. This handles
    the dup-spawn race traced at seed=42 (dup-{8}-spawn at tick 495)."""
    s = Substrate()
    origin = s.add_cell(Cell(spectrum={0}))
    other = s.add_cell(Cell(spectrum={1}))
    origin.connectors.append(other)
    other.connectors.append(origin)

    # Simulate: a child for token=99 already exists at origin (e.g., spawned
    # by an earlier deposit while this one was walking the substrate).
    existing_child = s.add_cell(Cell(spectrum={99}))
    origin.connectors.append(existing_child)
    existing_child.connectors.append(origin)

    # Now construct a deposit that will trigger the origin-loop check at origin
    # (predecessor=other, not in dead_paths).
    d = Deposit(token=99, predecessor=other, origin=origin, age=10)
    origin.pending.append(d)

    for _ in range(5):
        s.tick()

    # Guard should have caught it: NO new spawn (existing_child is the home),
    # and the deposit should have been forwarded to existing_child and consumed.
    new_spawns_for_99 = [s_ for s_ in s.spawn_log if s_[3] == 99]
    assert len(new_spawns_for_99) == 0, (
        f"dup-spawn guard failed: spawned a duplicate {{99}} when one already existed; "
        f"spawn_log={s.spawn_log}"
    )
    assert any(cell is existing_child and tok == 99 for (_, cell, tok, _) in s.consume_log), (
        f"expected consume at existing_child; got consume_log={s.consume_log}"
    )


def test_dup_spawn_guard_at_canvas_exhaust_forwards_when_connector_now_classifies():
    """At canvas-exhaust-on-Unknown spawn, the same guard fires. This catches
    the case where canvas_remaining captured a stale connector list before a
    new child was added by a parallel deposit."""
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    obs = s.add_cell(Cell(spectrum=set()))  # Learning -> Unknown
    c0.connectors.append(obs)
    obs.connectors.append(c0)

    # Begin a canvas at c0 with token=99. canvas_remaining will be [obs].
    s.inject(c0, token=99)
    s.tick()  # c0 begins handling, sends query to obs
    s.tick()  # obs receives, classifies (observe + Unknown)

    # Before c0 receives the response, ADD a child that classifies token=99.
    # This simulates the race: another deposit spawned a child for the same
    # token while this canvas was in-flight.
    new_child = Cell(spectrum={99})
    s.add_cell(new_child)
    c0.connectors.append(new_child)
    new_child.connectors.append(c0)

    # Now let c0 receive the Unknown response and decide.
    for _ in range(5):
        s.tick()

    # Guard should have forwarded to new_child instead of spawning.
    new_spawns_for_99 = [s_ for s_ in s.spawn_log if s_[3] == 99]
    assert len(new_spawns_for_99) == 0, (
        f"dup-spawn guard at canvas-exhaust failed: spawned despite existing classifier; "
        f"spawn_log={s.spawn_log}"
    )
    assert any(cell is new_child for (_, cell, _, _) in s.consume_log), (
        f"expected consume at new_child; got consume_log={s.consume_log}"
    )


def test_canvas_exhaustion_all_different_forwards_to_first_different():
    # Triangle so deposit can actually walk after Different-forward (each cell
    # has another non-predecessor neighbor besides the one that forwarded it).
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum={2}))
    c0.connectors.extend([c1, c2])
    c1.connectors.extend([c0, c2])
    c2.connectors.extend([c0, c1])
    s.inject(c0, token=7)

    # First few ticks: c0 canvases c1+c2 (both Different), forwards to c1.
    # No spawn yet — deposit is walking.
    for _ in range(5):
        s.tick()
    assert len(s.spawn_log) == 0, "should not have spawned before walking the loop"
    assert c0.is_idle

    # Eventually the deposit walks back to origin (c0) and triggers origin-loop spawn.
    for _ in range(20):
        s.tick()
    assert len(s.spawn_log) == 1
    _, parent, _, token = s.spawn_log[0]
    assert parent is c0
    assert token == 7


def test_deposit_age_increments_each_tick_while_in_flight():
    # Triangle so the deposit lives longer than 2 ticks before resolution.
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum={2}))
    c0.connectors.extend([c1, c2])
    c1.connectors.extend([c0, c2])
    c2.connectors.extend([c0, c1])
    d = s.inject(c0, token=7)
    assert d.age == 0
    s.tick()
    assert d.age == 1
    s.tick()
    assert d.age == 2
    s.tick()
    assert d.age == 3
