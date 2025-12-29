"""
Law Interface Protocol for Tick-Frame Physics Engine

This module defines the interface that all substrate laws must implement.
Laws are pluggable evolution rules that govern how the substrate state changes over ticks.
"""

from typing import Protocol, TypeVar, Dict, List, Tuple, Any
from abc import abstractmethod


# Generic state type - can be int, float, tuple, custom class, etc.
StateType = TypeVar('StateType')


class SubstrateLaw(Protocol[StateType]):
    """
    Protocol defining the interface for substrate evolution laws.

    Any law implementation must provide these methods to work with the unified engine.
    """

    # Metadata
    name: str
    """Human-readable name of this law (e.g., 'Law-000 XOR', 'Law-Quaternion')"""

    description: str
    """Brief description of what this law does"""

    # Core Evolution Methods

    @abstractmethod
    def initial_state(self, node_id: int) -> StateType:
        """
        Return the initial state for a newly created node.

        Args:
            node_id: The ID of the node being initialized

        Returns:
            The initial state value for this node

        Examples:
            - Binary law: return 0
            - Quaternion law: return (1.0, 0.0, 0.0, 0.0)
            - Energy law: return random energy value
        """
        ...

    @abstractmethod
    def evolve(
        self,
        graph: Dict[int, List[int]],
        state: Dict[int, StateType],
        tick: int
    ) -> Dict[int, StateType]:
        """
        Evolve the substrate state from tick t to tick t+1.

        This is the core evolution rule. Given the current graph topology
        and state at tick t, compute the new state at tick t+1.

        Args:
            graph: Dict mapping node_id -> list of neighbor node_ids
            state: Dict mapping node_id -> current state value
            tick: Current tick number (can be used for time-dependent rules)

        Returns:
            New state dict mapping node_id -> new state value

        Note:
            This function should be PURE - no side effects, no mutations.
            Return a new dict, don't modify the input.
        """
        ...

    @abstractmethod
    def should_grow(
        self,
        node_id: int,
        node_state: StateType,
        neighbors: List[int],
        neighbor_states: List[StateType]
    ) -> bool:
        """
        Determine if this node should spawn a new child node.

        Args:
            node_id: The ID of the node being evaluated
            node_state: Current state of this node
            neighbors: List of neighbor node IDs
            neighbor_states: List of neighbor state values (same order as neighbors)

        Returns:
            True if node should grow, False otherwise

        Examples:
            - XOR parity: return (sum of neighbor states) % 2 == 1
            - Quaternion: return imaginary_magnitude > threshold
            - Energy: return energy > spawn_threshold
        """
        ...

    # Visualization Methods

    @abstractmethod
    def to_3d_coords(self, state_value: StateType) -> Tuple[float, float, float]:
        """
        Convert a state value to 3D visualization coordinates.

        Args:
            state_value: The state value to visualize

        Returns:
            (x, y, z) tuple of floats

        Examples:
            - Binary: (0.0, 0.0, float(state))
            - Quaternion: (q[1], q[2], q[3])  # imaginary parts
            - Energy: (energy * cos(phase), energy * sin(phase), 0)
        """
        ...

    @abstractmethod
    def to_color(self, state_value: StateType) -> Tuple[int, int, int]:
        """
        Convert a state value to RGB color for visualization.

        Args:
            state_value: The state value to visualize

        Returns:
            (r, g, b) tuple of integers [0-255]

        Examples:
            - Binary: (255, 255, 255) if active else (0, 0, 0)
            - Quaternion: map imaginary parts to RGB channels
            - Energy: heat map (blue -> red)
        """
        ...

    # Optional: State Analysis Methods

    def state_summary(self, state_value: StateType) -> str:
        """
        Return a human-readable summary of a state value.

        Default implementation returns str(state_value).
        Override for prettier formatting.

        Args:
            state_value: The state to summarize

        Returns:
            String representation for logging/display
        """
        return str(state_value)

    def state_energy(self, state_value: StateType) -> float:
        """
        Return a scalar "energy" metric for this state.

        Used for analysis and statistics. Default returns 0.0.
        Override if your law has a meaningful energy concept.

        Args:
            state_value: The state to measure

        Returns:
            Scalar energy value
        """
        return 0.0


# Type alias for clarity
LawType = SubstrateLaw[StateType]
