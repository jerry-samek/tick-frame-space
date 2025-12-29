"""
Particle Observer
=================

Tracks adjacency loops and identity stability.

Concept:
In tick-frame physics, particles are stable collision patterns.
These manifest as:
- Loops in the adjacency graph (cycles)
- Stable degree patterns
- Persistent local structures

This observer tracks such patterns to identify "particle-like" entities.
"""

from typing import Optional, Set, Tuple
import networkx as nx
from collections import defaultdict
from .base import Observer


class ParticleObserver(Observer):
    """
    Observer for particle-like structures in the substrate.

    Tracks:
    - Adjacency loops (cycles)
    - Identity stability (entities with stable degree)
    - Persistent structures (local patterns that don't change)
    - Particle counts by type
    """

    def __init__(self, log_interval: int = 10, output_dir: Optional[str] = None):
        """
        Initialize ParticleObserver.

        Args:
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        super().__init__(name="Particle", log_interval=log_interval, output_dir=output_dir)

        # Track stable entities (degree hasn't changed)
        self.memory['stable_entities'] = {}  # entity_id -> ticks_stable
        self.memory['previous_degrees'] = {}  # entity_id -> degree

    def on_post_tick(self, state) -> None:
        """
        Compute particle metrics after each tick.

        Args:
            state: Current substrate state
        """
        tick = state.tick
        graph = state.adjacency

        # Count cycles (loops) in the graph
        num_triangles = sum(nx.triangles(graph).values()) // 3
        num_cycles = self._count_cycles(graph, max_length=6)

        # Track stable entities
        current_degrees = dict(graph.degree())
        stable_count = 0
        new_stable = {}

        for entity, degree in current_degrees.items():
            prev_degree = self.memory['previous_degrees'].get(entity, None)

            if prev_degree == degree:
                # Entity is stable
                ticks_stable = self.memory['stable_entities'].get(entity, 0) + 1
                new_stable[entity] = ticks_stable
                stable_count += 1
            else:
                # Entity changed, reset stability
                new_stable[entity] = 0

        self.memory['stable_entities'] = new_stable
        self.memory['previous_degrees'] = current_degrees

        # Classify particles by stability duration
        very_stable = sum(1 for t in new_stable.values() if t > 10)
        moderately_stable = sum(1 for t in new_stable.values() if 3 < t <= 10)
        weakly_stable = sum(1 for t in new_stable.values() if 0 < t <= 3)

        # Count persistent structures (triangles that appear repeatedly)
        persistent_structures = self._count_persistent_structures(graph)

        # Log if needed
        if self.should_log(tick):
            data = {
                'tick': tick,
                'num_triangles': num_triangles,
                'num_cycles': num_cycles,
                'stable_entities': stable_count,
                'very_stable': very_stable,
                'moderately_stable': moderately_stable,
                'weakly_stable': weakly_stable,
                'persistent_structures': persistent_structures,
            }

            self.log_csv('particle_metrics.csv', data)

            # Log summary
            summary = (
                f"[Particle t={tick}] "
                f"Triangles: {num_triangles}, "
                f"Cycles: {num_cycles}, "
                f"Stable: {stable_count} ({very_stable} very stable), "
                f"Persistent structures: {persistent_structures}\n"
            )
            self.log_text('particle_log.txt', summary)

    def _count_cycles(self, graph: nx.Graph, max_length: int = 6) -> int:
        """
        Count cycles up to max_length.

        Args:
            graph: Adjacency graph
            max_length: Maximum cycle length to count

        Returns:
            Total number of cycles
        """
        if graph.number_of_nodes() == 0:
            return 0

        # Use NetworkX's cycle_basis (finds fundamental cycles)
        try:
            cycles = nx.cycle_basis(graph)
            # Filter by length
            cycles = [c for c in cycles if len(c) <= max_length]
            return len(cycles)
        except:
            return 0

    def _count_persistent_structures(self, graph: nx.Graph) -> int:
        """
        Count structures (triangles) that have persisted for multiple ticks.

        Args:
            graph: Adjacency graph

        Returns:
            Number of persistent triangles
        """
        # Find all triangles
        triangles = set()
        for node in graph.nodes():
            neighbors = list(graph.neighbors(node))
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    if graph.has_edge(n1, n2):
                        # Found a triangle
                        triangle = tuple(sorted([node, n1, n2]))
                        triangles.add(triangle)

        # Track triangles in memory
        if 'previous_triangles' not in self.memory:
            self.memory['previous_triangles'] = set()
            self.memory['triangle_persistence'] = defaultdict(int)

        # Count persistent triangles
        persistent = triangles & self.memory['previous_triangles']

        # Update persistence counts
        for triangle in persistent:
            self.memory['triangle_persistence'][triangle] += 1

        # Clean up non-existent triangles
        for triangle in list(self.memory['triangle_persistence'].keys()):
            if triangle not in triangles:
                del self.memory['triangle_persistence'][triangle]

        self.memory['previous_triangles'] = triangles

        return len(persistent)
