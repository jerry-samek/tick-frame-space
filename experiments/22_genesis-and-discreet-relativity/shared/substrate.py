"""
Tick-Frame Substrate Engine
============================

Core substrate implementation for tick-frame experiments.
Provides minimal substrate state representation, update rule interface,
and engine with observer notification hooks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class SubstrateState:
    """
    Minimal representation of the universe at tick t.

    Attributes:
        entities: Map of entity IDs to their attributes
        adjacency: Graph structure representing entity relationships
        positions: Map of entity IDs to their 3D spatial coordinates (x, y, z)
        tick: Current tick counter
    """
    entities: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    adjacency: nx.Graph = field(default_factory=nx.Graph)
    positions: Dict[int, Tuple[float, float, float]] = field(default_factory=dict)
    tick: int = 0

    def copy(self) -> 'SubstrateState':
        """Create a deep copy of the substrate state."""
        return SubstrateState(
            entities={eid: attrs.copy() for eid, attrs in self.entities.items()},
            adjacency=self.adjacency.copy(),
            positions=self.positions.copy(),
            tick=self.tick
        )


class UpdateRule(ABC):
    """
    Abstract base class for substrate update rules.

    Defines the substrate transition: A(t+1) = U(A(t))

    This is the only place where adjacency changes occur.
    Update rules are:
    - Local (depend only on local adjacency)
    - Memoryless (no internal state)
    - Synchronous (all updates happen atomically)
    - Geometry-free (no coordinates, only adjacency)
    """

    @abstractmethod
    def expand(self, state: SubstrateState) -> SubstrateState:
        """
        Expansion phase: add new entities or edges.

        Args:
            state: Current substrate state

        Returns:
            Modified state after expansion
        """
        pass

    @abstractmethod
    def mutate(self, state: SubstrateState) -> SubstrateState:
        """
        Mutation phase: modify entity attributes or adjacency.

        Args:
            state: Current substrate state

        Returns:
            Modified state after mutation
        """
        pass

    @abstractmethod
    def bias(self, state: SubstrateState) -> SubstrateState:
        """
        Bias phase: apply asymmetric transformations.

        Args:
            state: Current substrate state

        Returns:
            Modified state after bias application
        """
        pass

    def step(self, state: SubstrateState) -> SubstrateState:
        """
        Execute one full update step: expand → mutate → bias.

        Args:
            state: Current substrate state

        Returns:
            New substrate state at t+1
        """
        # Make a copy to avoid modifying the input
        new_state = state.copy()

        # Apply transformations in sequence
        new_state = self.expand(new_state)
        new_state = self.mutate(new_state)
        new_state = self.bias(new_state)

        # Increment tick counter
        new_state.tick += 1

        return new_state


class SubstrateEngine:
    """
    Substrate execution engine with observer support.

    Responsibilities:
    - Hold current SubstrateState
    - Apply update rule each tick
    - Notify observers before and after each tick
    """

    def __init__(self, initial_state: SubstrateState, update_rule: UpdateRule):
        """
        Initialize the substrate engine.

        Args:
            initial_state: Starting substrate state
            update_rule: Update rule implementation
        """
        self.state = initial_state
        self.update_rule = update_rule
        self.observers: List['Observer'] = []

    def add_observer(self, observer: 'Observer') -> None:
        """
        Attach an observer to the engine.

        Args:
            observer: Observer instance to attach
        """
        self.observers.append(observer)

    def run(self, max_ticks: int) -> None:
        """
        Run the substrate for a specified number of ticks.

        Args:
            max_ticks: Maximum number of ticks to execute
        """
        for _ in range(max_ticks):
            # Notify observers before tick
            self._notify_pre_tick()

            # Apply update rule
            self.state = self.update_rule.step(self.state)

            # Notify observers after tick
            self._notify_post_tick()

    def _notify_pre_tick(self) -> None:
        """Notify all observers before tick execution."""
        for observer in self.observers:
            observer.on_pre_tick(self.state)

    def _notify_post_tick(self) -> None:
        """Notify all observers after tick execution."""
        for observer in self.observers:
            observer.on_post_tick(self.state)


# Import guard to prevent circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from observers.base import Observer
