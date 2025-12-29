"""
Entropy Observer
================

Tracks entropy measures in the substrate: S(t).

Entropy concepts:
- Graph entropy: Shannon entropy of degree distribution
- Structural entropy: Information content of graph topology
- Entropy growth: Second law of thermodynamics in substrate
"""

from typing import Optional
import networkx as nx
from collections import Counter
import math
from .base import Observer


class EntropyObserver(Observer):
    """
    Observer for entropy and information-theoretic metrics.

    Tracks:
    - S(t): Graph entropy (degree distribution)
    - Structural complexity
    - Entropy production rate
    - Reachable states estimate
    """

    def __init__(self, log_interval: int = 10, output_dir: Optional[str] = None):
        """
        Initialize EntropyObserver.

        Args:
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        super().__init__(name="Entropy", log_interval=log_interval, output_dir=output_dir)

        # Track entropy over time
        self.memory['entropy_history'] = []
        self.memory['complexity_history'] = []

    def on_post_tick(self, state) -> None:
        """
        Compute entropy metrics after each tick.

        Args:
            state: Current substrate state
        """
        tick = state.tick
        graph = state.adjacency

        # Compute degree distribution entropy
        degree_entropy = self._compute_degree_entropy(graph)

        # Compute structural complexity (number of unique local patterns)
        structural_complexity = self._compute_structural_complexity(graph)

        # Store in memory
        self.memory['entropy_history'].append(degree_entropy)
        self.memory['complexity_history'].append(structural_complexity)

        # Compute entropy production rate
        if len(self.memory['entropy_history']) > 1:
            entropy_rate = (
                self.memory['entropy_history'][-1] - self.memory['entropy_history'][-2]
            )
        else:
            entropy_rate = 0.0

        # Estimate reachable states (exponential of entropy)
        reachable_states = math.exp(degree_entropy) if degree_entropy > 0 else 1.0

        # Log if needed
        if self.should_log(tick):
            data = {
                'tick': tick,
                'degree_entropy': degree_entropy,
                'structural_complexity': structural_complexity,
                'entropy_rate': entropy_rate,
                'reachable_states': reachable_states,
            }

            self.log_csv('entropy_metrics.csv', data)

            # Log summary
            summary = (
                f"[Entropy t={tick}] "
                f"S={degree_entropy:.4f}, "
                f"Complexity={structural_complexity}, "
                f"dS/dt={entropy_rate:.4f}, "
                f"Reachable states={reachable_states:.2e}\n"
            )
            self.log_text('entropy_log.txt', summary)

    def _compute_degree_entropy(self, graph: nx.Graph) -> float:
        """
        Compute Shannon entropy of degree distribution.

        S = -Σ p(k) log p(k)

        Args:
            graph: Adjacency graph

        Returns:
            Degree distribution entropy
        """
        if graph.number_of_nodes() == 0:
            return 0.0

        # Get degree distribution
        degrees = [d for n, d in graph.degree()]
        degree_counts = Counter(degrees)
        total = sum(degree_counts.values())

        # Compute Shannon entropy
        entropy = 0.0
        for count in degree_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log(p)

        return entropy

    def _compute_structural_complexity(self, graph: nx.Graph) -> int:
        """
        Compute structural complexity as number of unique local patterns.

        Counts unique 2-hop neighborhoods (ego graphs).

        Args:
            graph: Adjacency graph

        Returns:
            Number of unique local patterns
        """
        if graph.number_of_nodes() == 0:
            return 0

        # Sample up to 100 nodes for efficiency
        nodes_to_sample = min(100, graph.number_of_nodes())
        sample_nodes = list(graph.nodes())[:nodes_to_sample]

        # Extract local patterns (degree sequences of 1-hop neighbors)
        patterns = set()
        for node in sample_nodes:
            neighbors = list(graph.neighbors(node))
            if neighbors:
                neighbor_degrees = tuple(sorted([graph.degree(n) for n in neighbors]))
                patterns.add(neighbor_degrees)

        return len(patterns)
