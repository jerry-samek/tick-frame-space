from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from typing import Any

from cell import Cell, Deposit, Response


@dataclass(order=True)
class _Event:
    arrival_tick: int
    sequence_id: int
    payload: Any = field(compare=False)


@dataclass
class _Query:
    from_cell: Cell
    to_cell: Cell
    token: int


@dataclass
class _Response:
    from_cell: Cell
    to_cell: Cell
    response: Response


class Substrate:
    def __init__(self) -> None:
        self.tick_count: int = 0
        self.cells: list[Cell] = []
        self._events: list[_Event] = []
        self._event_seq: int = 0
        self.spawn_log: list[tuple[int, Cell, Cell, int]] = []
        self.consume_log: list[tuple[int, Cell, int, int]] = []

    def add_cell(self, cell: Cell) -> Cell:
        cell.creation_order = len(self.cells)
        self.cells.append(cell)
        return cell

    def inject(self, cell: Cell, token: int) -> Deposit:
        d = Deposit(token=token, predecessor=None, origin=cell, age=0)
        cell.pending.append(d)
        return d

    def _enqueue(self, arrival_tick: int, payload: Any) -> None:
        heapq.heappush(self._events, _Event(arrival_tick, self._event_seq, payload))
        self._event_seq += 1

    def tick(self) -> None:
        self.tick_count += 1
        while self._events and self._events[0].arrival_tick == self.tick_count:
            ev = heapq.heappop(self._events)
            self._process_event(ev.payload)
        for cell in sorted(self.cells, key=lambda c: c.creation_order):
            if cell.is_idle and cell.pending:
                deposit = cell.pending.popleft()
                self._begin_handling(cell, deposit)
        for cell in self.cells:
            if cell.current_deposit is not None:
                cell.current_deposit.age += 1
            for d in cell.pending:
                d.age += 1

    def _process_event(self, payload) -> None:
        if isinstance(payload, _Query):
            response = payload.to_cell.classify(payload.token)
            self._enqueue(self.tick_count + 1, _Response(
                from_cell=payload.to_cell,
                to_cell=payload.from_cell,
                response=response,
            ))
        elif isinstance(payload, _Response):
            self._handle_response(payload)

    def _begin_handling(self, cell: Cell, deposit: Deposit) -> None:
        if deposit.token in cell.spectrum:
            self._consume(cell, deposit)
            return
        # Origin-loop check: D returned to origin via a "real" forward
        # (not a leaf bounce). True closed loop with no home found.
        if (cell is deposit.origin
                and deposit.predecessor is not None
                and deposit.predecessor not in deposit.dead_paths):
            # Dup-spawn race guard: between this deposit's first canvas at
            # origin and now, another deposit may have spawned a child whose
            # spectrum classifies this token. The earlier canvas captured a
            # stale connector list. Check current connectors directly for a
            # Same match before committing to a spawn. (Direct spectrum
            # access is consistent with the existing self-check above; the
            # canvas protocol is preserved for non-degenerate routing.)
            for n in cell.connectors:
                if deposit.token in n.spectrum:
                    deposit.chain_stack.append(cell)
                    n.pending.append(deposit)
                    return
            self._spawn(cell, deposit)
            return
        cell.current_deposit = deposit
        cell.canvas_responses = []
        cell.canvas_remaining = self._canvas_order(
            cell, deposit.predecessor, deposit.dead_paths,
        )
        if not cell.canvas_remaining:
            if deposit.predecessor is not None:
                self._bounce(cell)
            else:
                # Degenerate: fresh injection at isolated cell.
                self._spawn(cell, deposit)
                self._reset_canvas_state(cell)
            return
        self._send_next_query(cell)

    def _bounce(self, cell: Cell) -> None:
        """Send the deposit back to its predecessor; mark this cell as a dead path.
        Pops the chain_stack so the receiving cell sees its original chain
        predecessor (not this leaf) as predecessor on re-handling."""
        deposit = cell.current_deposit
        target = deposit.predecessor
        deposit.dead_paths.add(cell)
        deposit.chain_stack.pop()
        target.pending.append(deposit)
        self._reset_canvas_state(cell)

    def _canvas_order(self, cell: Cell, predecessor, dead_paths) -> list[Cell]:
        n = len(cell.connectors)
        if n == 0:
            return []
        start = cell.next_canvas_index % n
        ordered = [cell.connectors[(start + i) % n] for i in range(n)]
        cell.next_canvas_index = (start + 1) % n
        return [c for c in ordered if c is not predecessor and c not in dead_paths]

    def _send_next_query(self, cell: Cell) -> None:
        next_neighbor = cell.canvas_remaining.pop(0)
        cell.canvas_in_flight = next_neighbor
        self._enqueue(self.tick_count + 1, _Query(
            from_cell=cell,
            to_cell=next_neighbor,
            token=cell.current_deposit.token,
        ))

    def _handle_response(self, payload: _Response) -> None:
        cell = payload.to_cell
        responder = payload.from_cell
        cell.canvas_responses.append((responder, payload.response))
        cell.canvas_in_flight = None
        if payload.response == Response.SAME:
            self._forward(cell, responder)
        elif cell.canvas_remaining:
            self._send_next_query(cell)
        else:
            self._decide_after_canvas(cell)

    def _forward(self, cell: Cell, target: Cell) -> None:
        deposit = cell.current_deposit
        deposit.chain_stack.append(cell)
        target.pending.append(deposit)
        self._reset_canvas_state(cell)

    def _reset_canvas_state(self, cell: Cell) -> None:
        cell.current_deposit = None
        cell.canvas_responses = []
        cell.canvas_remaining = []
        cell.canvas_in_flight = None

    def _decide_after_canvas(self, cell: Cell) -> None:
        # Prefer Different over Unknown: Different responders are routable; Unknown
        # responders are Learning observers — they observed the query but can't route.
        # Spawn-on-Unknown only fires when *all* responders are Unknown (no path forward).
        deposit = cell.current_deposit
        responses = cell.canvas_responses
        first_different = next(
            (n for (n, r) in responses if r == Response.DIFFERENT),
            None,
        )
        if first_different is not None:
            self._forward(cell, first_different)
            return
        has_unknown = any(r == Response.UNKNOWN for (_, r) in responses)
        if has_unknown:
            # Dup-spawn race guard (same as origin-loop case): the canvas
            # used a stale connector snapshot; another deposit may have
            # spawned a child for this token since this canvas began.
            for n in cell.connectors:
                if deposit.token in n.spectrum:
                    self._forward(cell, n)
                    return
            self._spawn(cell, deposit)
            self._reset_canvas_state(cell)
            return
        raise AssertionError("canvas exhausted with no Same/Different/Unknown")

    def _consume(self, cell: Cell, deposit: Deposit) -> None:
        self.consume_log.append((self.tick_count, cell, deposit.token, deposit.age))

    def _spawn(self, cell: Cell, deposit: Deposit) -> None:
        new_cell = Cell(spectrum={deposit.token})
        new_cell.connectors.append(cell)
        cell.connectors.append(new_cell)
        self.add_cell(new_cell)
        self.spawn_log.append((self.tick_count, cell, new_cell, deposit.token))
