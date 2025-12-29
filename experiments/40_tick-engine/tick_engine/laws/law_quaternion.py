"""
Law-Quaternion: 3D Movement via Quaternion Algebra

Extended law using quaternion state space for 3D spatial dynamics.
Not the theoretical Law-000 baseline, but an experimental evolution rule.

State Type: Tuple[float, float, float, float] (quaternion w, x, y, z)

Evolution Rule:
    q'(n) = normalize(q(n) + dq)

Where:
    dq = 0.1 * (chaos * e_0 + sum(neighbor.xyz))
    chaos = ±1 alternating with tick
    normalize ensures |q| = 1
"""

import math
from typing import Dict, List, Tuple


# Type alias for quaternion
Quaternion = Tuple[float, float, float, float]


class LawQuaternion:
    """
    Law-Quaternion: 3D Movement via Quaternion Algebra

    Uses quaternion state space (w, x, y, z) to represent 3D position/orientation.
    Imaginary parts (x, y, z) drive movement, real part (w) stabilizes.
    """

    # Metadata
    name = "Law-Quaternion"
    description = "3D movement via quaternion algebra with chaos injection"

    # State type
    StateType = Quaternion

    def initial_state(self, node_id: int) -> Quaternion:
        """
        New nodes start at identity quaternion (1, 0, 0, 0).

        Identity represents rest state / ground state.
        """
        return (1.0, 0.0, 0.0, 0.0)

    def evolve(
        self,
        graph: Dict[int, List[int]],
        state: Dict[int, Quaternion],
        tick: int
    ) -> Dict[int, Quaternion]:
        """
        Quaternion evolution rule.

        For each node:
        1. Sum imaginary parts of neighbors → direction vector
        2. Add chaos to real part
        3. Scale by 0.1 for smooth evolution
        4. Add to current quaternion
        5. Renormalize to unit sphere
        """
        new_state = {}

        # Chaos injector: ±1 alternating with tick parity
        chaos = -1 if (tick & 1) else +1

        for node, neighbors in graph.items():
            # Compute quaternion displacement from neighbors
            dq = [0.0, 0.0, 0.0, 0.0]

            for n in neighbors:
                if n in state:
                    w, x, y, z = state[n]
                    # Imaginary parts of neighbors create directional drift
                    dq[1] += x  # i component
                    dq[2] += y  # j component
                    dq[3] += z  # k component

            # Chaos adds to real part (w component)
            dq[0] += 0.05 * chaos

            # Scale step size for smooth evolution
            dq = tuple(component * 0.1 for component in dq)

            # Update: q' = q + dq
            current_q = state[node]
            updated_q = self._q_add(current_q, dq)

            # Renormalize to unit sphere (fundamental constraint)
            new_state[node] = self._q_normalize(updated_q)

        return new_state

    def should_grow(
        self,
        node_id: int,
        node_state: Quaternion,
        neighbors: List[int],
        neighbor_states: List[Quaternion]
    ) -> bool:
        """
        Growth rule: spawn if imaginary magnitude of neighbors exceeds threshold.

        Threshold at 0.5: nodes with significant spatial displacement grow.
        """
        imaginary_sum = 0.0
        for q in neighbor_states:
            w, x, y, z = q
            # Magnitude of imaginary part
            imaginary_sum += math.sqrt(x*x + y*y + z*z)

        return imaginary_sum > 0.5

    def to_3d_coords(self, state_value: Quaternion) -> Tuple[float, float, float]:
        """
        Visualization: use imaginary parts (x, y, z) as 3D coordinates.

        This maps quaternion state directly to spatial position.
        """
        w, x, y, z = state_value
        return (x, y, z)

    def to_color(self, state_value: Quaternion) -> Tuple[int, int, int]:
        """
        Visualization: map imaginary parts to RGB channels.

        Absolute values scaled to [0, 255].
        """
        w, x, y, z = state_value
        r = int(abs(x) * 255)
        g = int(abs(y) * 255)
        b = int(abs(z) * 255)
        return (r, g, b)

    def state_summary(self, state_value: Quaternion) -> str:
        """Human-readable quaternion"""
        w, x, y, z = state_value
        return f"q=({w:.3f}, {x:.3f}, {y:.3f}, {z:.3f})"

    def state_energy(self, state_value: Quaternion) -> float:
        """
        Energy = magnitude of imaginary part.

        Represents spatial displacement from ground state.
        """
        w, x, y, z = state_value
        return math.sqrt(x*x + y*y + z*z)

    # Helper functions

    def _q_add(self, q: Quaternion, dq: Tuple) -> Quaternion:
        """Add two quaternions component-wise"""
        return (
            q[0] + dq[0],
            q[1] + dq[1],
            q[2] + dq[2],
            q[3] + dq[3]
        )

    def _q_normalize(self, q: Quaternion) -> Quaternion:
        """Normalize quaternion to unit magnitude"""
        w, x, y, z = q
        magnitude = math.sqrt(w*w + x*x + y*y + z*z)

        if magnitude == 0.0:
            return (1.0, 0.0, 0.0, 0.0)  # identity if zero

        return (
            w / magnitude,
            x / magnitude,
            y / magnitude,
            z / magnitude
        )


# Convenience function for creating initial graphs
def create_3d_seed_graph() -> Tuple[Dict[int, List[int]], Dict[int, Quaternion]]:
    """
    Create a small seed graph with quaternions aligned to different axes.

    Graph: 0 — 1 — 2 (line)
    States: 0=identity, 1=i-axis, 2=j-axis

    Returns:
        (graph, initial_state) tuple
    """
    graph = {
        0: [1],
        1: [0, 2],
        2: [1]
    }

    initial_state = {
        0: (1.0, 0.0, 0.0, 0.0),  # identity (ground state)
        1: (0.0, 1.0, 0.0, 0.0),  # i-axis (x direction)
        2: (0.0, 0.0, 1.0, 0.0)   # j-axis (y direction)
    }

    return graph, initial_state
