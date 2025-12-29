"""
Law-000: XOR Parity Rule

Theoretical baseline law from docs/theory/39_0 Law‑000 XOR Parity Rule.md

This is the minimal, parameter-free evolution rule for a discrete substrate.
State evolution follows pure XOR parity logic with chaos injection.

State Type: int (binary {0, 1})

Evolution Rule:
    S_{t+1}(n) = S_t(n) ⊕ P_t(n) ⊕ chaos(t)

Where:
    P_t(n) = (sum of active neighbors) mod 2
    chaos(t) = t mod 2
"""

from typing import Dict, List, Tuple


class Law000_XOR:
    """
    Law-000: XOR Parity Evolution

    The theoretical baseline law - pure binary cellular automaton with:
    - Binary state {0, 1}
    - XOR parity update rule
    - Chaos injection based on tick parity
    - No parameters, no thresholds
    """

    # Metadata
    name = "Law-000 XOR"
    description = "Theoretical baseline: binary XOR parity with chaos injection"

    # State type
    StateType = int

    def initial_state(self, node_id: int) -> int:
        """
        New nodes start inactive (0).

        Different initial states can be set manually for experiments.
        """
        return 0

    def evolve(
        self,
        graph: Dict[int, List[int]],
        state: Dict[int, int],
        tick: int
    ) -> Dict[int, int]:
        """
        Core XOR parity evolution rule.

        For each node n:
        1. Count active neighbors: K(n) = sum(state[neighbor])
        2. Compute parity: P(n) = K(n) mod 2
        3. Add chaos: chaos = tick mod 2
        4. Update: state'(n) = state(n) XOR P(n) XOR chaos

        This is equation (3.1) from theory doc 39_0.
        """
        new_state = {}

        # Chaos injector: alternates 0,1,0,1,... with tick
        chaos = tick & 1  # equivalent to tick mod 2

        for node, neighbors in graph.items():
            # Count active neighbors
            active_neighbors = sum(state[n] for n in neighbors if n in state)

            # Compute parity
            parity = active_neighbors % 2

            # XOR update: state XOR parity XOR chaos
            new_state[node] = state[node] ^ parity ^ chaos

        return new_state

    def should_grow(
        self,
        node_id: int,
        node_state: int,
        neighbors: List[int],
        neighbor_states: List[int]
    ) -> bool:
        """
        Growth rule: spawn new node if parity of neighbors is odd.

        This follows the pattern: growth when parity = 1.
        """
        active_neighbors = sum(neighbor_states)
        parity = active_neighbors % 2
        return parity == 1

    def to_3d_coords(self, state_value: int) -> Tuple[float, float, float]:
        """
        Visualization: map binary state to z-axis.

        Active (1) nodes at z=1.0, inactive (0) nodes at z=0.0.
        x,y could be derived from node topology or left at origin.
        """
        return (0.0, 0.0, float(state_value))

    def to_color(self, state_value: int) -> Tuple[int, int, int]:
        """
        Visualization: white for active, black for inactive.
        """
        if state_value == 1:
            return (255, 255, 255)  # white
        else:
            return (0, 0, 0)  # black

    def state_summary(self, state_value: int) -> str:
        """Human-readable state"""
        return "active" if state_value == 1 else "inactive"

    def state_energy(self, state_value: int) -> float:
        """Energy = state value (0 or 1)"""
        return float(state_value)


# Convenience function for creating initial graphs
def create_line_graph(n: int) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
    """
    Create a line graph: 0 — 1 — 2 — ... — (n-1)

    Args:
        n: Number of nodes

    Returns:
        (graph, initial_state) tuple
    """
    graph = {}
    for i in range(n):
        neighbors = []
        if i > 0:
            neighbors.append(i - 1)
        if i < n - 1:
            neighbors.append(i + 1)
        graph[i] = neighbors

    # All start inactive except middle node
    initial_state = {i: 0 for i in range(n)}
    initial_state[n // 2] = 1  # activate middle

    return graph, initial_state


def create_cycle_graph(n: int) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
    """
    Create a cycle graph: 0 — 1 — 2 — ... — (n-1) — 0

    Args:
        n: Number of nodes

    Returns:
        (graph, initial_state) tuple
    """
    graph = {}
    for i in range(n):
        prev_node = (i - 1) % n
        next_node = (i + 1) % n
        graph[i] = [prev_node, next_node]

    # Activate first node only
    initial_state = {i: 0 for i in range(n)}
    initial_state[0] = 1

    return graph, initial_state
