from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Response(Enum):
    SAME = "same"
    DIFFERENT = "different"
    UNKNOWN = "unknown"


class State(Enum):
    LEARNING = "learning"
    CRYSTALLIZED = "crystallized"


@dataclass(eq=False)
class Cell:
    spectrum: set[int]
    connectors: list["Cell"] = field(default_factory=list)
    pending: deque = field(default_factory=deque)
    next_canvas_index: int = 0
    creation_order: int = -1
    current_deposit: Optional["Deposit"] = None
    canvas_responses: list = field(default_factory=list)
    canvas_remaining: list = field(default_factory=list)
    canvas_in_flight: Optional["Cell"] = None
    obs_counter: Counter = field(default_factory=Counter)
    state: State = State.LEARNING
    learning_threshold: int = 50
    crystallization_size: int = 3

    def __post_init__(self) -> None:
        # Cells created with a preset spectrum start Crystallized;
        # cells created empty start Learning.
        if self.spectrum:
            self.state = State.CRYSTALLIZED

    @property
    def is_idle(self) -> bool:
        return self.current_deposit is None

    def observe(self, token: int) -> None:
        self.obs_counter[token] += 1
        if (self.state == State.LEARNING
                and sum(self.obs_counter.values()) >= self.learning_threshold):
            self.crystallize()

    def crystallize(self) -> None:
        top_k = self.obs_counter.most_common(self.crystallization_size)
        self.spectrum = {token for (token, _) in top_k}
        self.state = State.CRYSTALLIZED

    def classify(self, token: int) -> Response:
        self.observe(token)
        if self.state == State.LEARNING:
            return Response.UNKNOWN
        if token in self.spectrum:
            return Response.SAME
        return Response.DIFFERENT


class Deposit:
    """A walking deposit. `chain_stack` is the stack of cells that have forwarded
    this deposit (most-recent on top). `predecessor` is a read-only view of the
    top of the stack — the cell that put this deposit into the current cell's
    processing chain.

    The chain_stack distinction matters when a deposit forwards to a leaf that
    bounces back: the bounce pops the leaf's parent off the stack, restoring
    the receiving cell's view of "the cell that originally chained me here."
    Without the stack, a leaf-bounce would leave the receiving cell unable to
    distinguish "the leaf that just bounced" from "the cell that originally
    forwarded the deposit to me," and canvas could route the deposit backward
    along its original path. (See trace_4spawn.py for the bug this prevents.)
    """

    def __init__(self, token, predecessor=None, origin=None, age=0,
                 chain_stack=None, dead_paths=None):
        self.token = token
        self.origin = origin
        self.age = age
        if chain_stack is not None:
            self.chain_stack = chain_stack
        elif predecessor is not None:
            self.chain_stack = [predecessor]
        else:
            self.chain_stack = []
        self.dead_paths = dead_paths if dead_paths is not None else set()

    @property
    def predecessor(self):
        return self.chain_stack[-1] if self.chain_stack else None
