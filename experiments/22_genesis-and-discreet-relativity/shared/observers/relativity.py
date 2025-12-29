"""
Relativity Observer
===================

Tracks worldlines and causal classification in the substrate.

Key concepts:
- Worldlines: temporal traces of entities through ticks
- Causal classification: timelike, spacelike, lightlike adjacencies
- Causal cones: past/future light cones for entities
- Proper time: accumulated ticks along worldlines
"""

from typing import Optional, Dict, Set, Tuple
import networkx as nx
from collections import defaultdict
from .base import Observer


class RelativityObserver(Observer):
    """
    Observer for relativity metrics: worldlines and causal structure.

    Tracks:
    - Entity worldlines (temporal identity chains)
    - Causal classification of adjacencies
    - Causal cone sizes
    - Proper time accumulation
    """

    def __init__(self, log_interval: int = 10, output_dir: Optional[str] = None):
        """
        Initialize RelativityObserver.

        Args:
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        super().__init__(name="Relativity", log_interval=log_interval, output_dir=output_dir)

        # Track entity worldlines: entity_id -> [tick1, tick2, ...]
        self.memory['worldlines'] = defaultdict(list)

        # Track previous graph state for causal analysis
        self.memory['previous_graph'] = None
        self.memory['previous_entities'] = set()

    def on_post_tick(self, state) -> None:
        """
        Compute relativity metrics after each tick.

        Args:
            state: Current substrate state
        """
        tick = state.tick
        graph = state.adjacency
        current_entities = set(state.entities.keys())

        # Update worldlines for all current entities
        for entity_id in current_entities:
            self.memory['worldlines'][entity_id].append(tick)

        # Classify adjacencies as timelike, spacelike, or lightlike
        if self.memory['previous_graph'] is not None:
            causal_stats = self._classify_causal_structure(
                self.memory['previous_graph'],
                graph,
                self.memory['previous_entities'],
                current_entities
            )
        else:
            causal_stats = {
                'timelike_edges': 0,
                'spacelike_edges': 0,
                'lightlike_edges': 0,
                'new_entities': len(current_entities),
                'destroyed_entities': 0,
            }

        # Compute average worldline length
        worldline_lengths = [len(wl) for wl in self.memory['worldlines'].values()]
        avg_worldline_length = sum(worldline_lengths) / len(worldline_lengths) if worldline_lengths else 0
        max_worldline_length = max(worldline_lengths) if worldline_lengths else 0

        # Compute causal cone sizes (how many entities are reachable within distance d)
        if graph.number_of_nodes() > 0:
            sample_entity = list(graph.nodes())[0]
            causal_cone_size = self._compute_causal_cone_size(graph, sample_entity, max_distance=5)
        else:
            causal_cone_size = 0

        # Store current state for next tick
        self.memory['previous_graph'] = graph.copy()
        self.memory['previous_entities'] = current_entities.copy()

        # Log if needed
        if self.should_log(tick):
            data = {
                'tick': tick,
                'num_entities': len(current_entities),
                'avg_worldline_length': avg_worldline_length,
                'max_worldline_length': max_worldline_length,
                'causal_cone_size': causal_cone_size,
                **causal_stats,
            }

            self.log_csv('relativity_metrics.csv', data)

            # Log summary
            summary = (
                f"[Relativity t={tick}] "
                f"Worldlines: {len(self.memory['worldlines'])}, "
                f"Avg length: {avg_worldline_length:.2f}, "
                f"Causal cone: {causal_cone_size}\n"
            )
            self.log_text('relativity_log.txt', summary)

    def _classify_causal_structure(
        self,
        prev_graph: nx.Graph,
        curr_graph: nx.Graph,
        prev_entities: Set[int],
        curr_entities: Set[int]
    ) -> Dict[str, int]:
        """
        Classify edges as timelike, spacelike, or lightlike.

        Heuristic:
        - Timelike: edges between entities that existed in previous tick
        - Spacelike: edges between newly created entities
        - Lightlike: edges connecting old and new entities

        Args:
            prev_graph: Graph at t-1
            curr_graph: Graph at t
            prev_entities: Entity IDs at t-1
            curr_entities: Entity IDs at t

        Returns:
            Dictionary of causal statistics
        """
        persistent_entities = prev_entities & curr_entities
        new_entities = curr_entities - prev_entities
        destroyed_entities = prev_entities - curr_entities

        timelike_edges = 0
        spacelike_edges = 0
        lightlike_edges = 0

        for u, v in curr_graph.edges():
            if u in persistent_entities and v in persistent_entities:
                timelike_edges += 1
            elif u in new_entities and v in new_entities:
                spacelike_edges += 1
            else:
                lightlike_edges += 1

        return {
            'timelike_edges': timelike_edges,
            'spacelike_edges': spacelike_edges,
            'lightlike_edges': lightlike_edges,
            'new_entities': len(new_entities),
            'destroyed_entities': len(destroyed_entities),
        }

    def _compute_causal_cone_size(self, graph: nx.Graph, entity: int, max_distance: int = 5) -> int:
        """
        Compute size of causal cone (entities reachable within max_distance).

        Args:
            graph: Adjacency graph
            entity: Source entity
            max_distance: Maximum distance to consider

        Returns:
            Number of entities in causal cone
        """
        if entity not in graph:
            return 0

        # BFS to find all nodes within max_distance
        visited = {entity}
        queue = [(entity, 0)]
        cone_size = 1

        while queue:
            node, dist = queue.pop(0)

            if dist >= max_distance:
                continue

            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    cone_size += 1

        return cone_size
