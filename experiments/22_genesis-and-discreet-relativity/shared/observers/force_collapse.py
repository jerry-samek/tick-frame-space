"""
Force Collapse Observer
========================

Tracks adjacency bias signatures that may represent emergent forces.

Concept:
In tick-frame physics, forces emerge from asymmetries in adjacency updates.
- Gravity: Preferential attachment (high-degree bias)
- Electromagnetism: Charge-like attributes and repulsion/attraction
- Strong force: Local clustering pressure
- Weak force: Decay patterns (edge removal)

This observer detects bias patterns in the substrate evolution.
"""

from typing import Optional, Dict
import networkx as nx
from collections import defaultdict
from .base import Observer


class ForceCollapseObserver(Observer):
    """
    Observer for force-like bias signatures in substrate updates.

    Tracks:
    - Degree bias (preferential attachment strength)
    - Clustering bias (local vs. global connectivity)
    - Asymmetry in edge creation/destruction
    - Spatial correlation patterns
    """

    def __init__(self, log_interval: int = 10, output_dir: Optional[str] = None):
        """
        Initialize ForceCollapseObserver.

        Args:
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        super().__init__(name="ForceCollapse", log_interval=log_interval, output_dir=output_dir)

        # Track previous state for delta analysis
        self.memory['previous_graph'] = None
        self.memory['degree_bias_history'] = []
        self.memory['clustering_bias_history'] = []

    def on_post_tick(self, state) -> None:
        """
        Compute force bias metrics after each tick.

        Args:
            state: Current substrate state
        """
        tick = state.tick
        graph = state.adjacency

        # Compute degree bias (preferential attachment strength)
        degree_bias = self._compute_degree_bias(graph)

        # Compute clustering bias
        clustering_bias = self._compute_clustering_bias(graph)

        # Compute edge asymmetry (creation vs. destruction)
        if self.memory['previous_graph'] is not None:
            edge_asymmetry = self._compute_edge_asymmetry(
                self.memory['previous_graph'],
                graph
            )
        else:
            edge_asymmetry = {
                'edges_added': 0,
                'edges_removed': 0,
                'asymmetry_ratio': 0.0,
            }

        # Compute spatial correlation (do neighbors of neighbors connect?)
        spatial_correlation = self._compute_spatial_correlation(graph)

        # Store in memory
        self.memory['degree_bias_history'].append(degree_bias)
        self.memory['clustering_bias_history'].append(clustering_bias)
        self.memory['previous_graph'] = graph.copy()

        # Compute drift in bias patterns
        degree_bias_drift = self._compute_variance(self.memory['degree_bias_history'])
        clustering_bias_drift = self._compute_variance(self.memory['clustering_bias_history'])

        # Log if needed
        if self.should_log(tick):
            data = {
                'tick': tick,
                'degree_bias': degree_bias,
                'clustering_bias': clustering_bias,
                'edges_added': edge_asymmetry['edges_added'],
                'edges_removed': edge_asymmetry['edges_removed'],
                'asymmetry_ratio': edge_asymmetry['asymmetry_ratio'],
                'spatial_correlation': spatial_correlation,
                'degree_bias_drift': degree_bias_drift,
                'clustering_bias_drift': clustering_bias_drift,
            }

            self.log_csv('force_collapse_metrics.csv', data)

            # Log summary
            summary = (
                f"[ForceCollapse t={tick}] "
                f"Degree bias: {degree_bias:.4f}, "
                f"Clustering bias: {clustering_bias:.4f}, "
                f"Edge +/-: {edge_asymmetry['edges_added']}/{edge_asymmetry['edges_removed']}, "
                f"Spatial corr: {spatial_correlation:.4f}\n"
            )
            self.log_text('force_collapse_log.txt', summary)

    def _compute_degree_bias(self, graph: nx.Graph) -> float:
        """
        Compute degree bias (preferential attachment strength).

        Measures correlation between node degree and neighbor degrees.
        High correlation = strong preferential attachment (gravity-like).

        Args:
            graph: Adjacency graph

        Returns:
            Degree bias coefficient
        """
        if graph.number_of_edges() == 0:
            return 0.0

        try:
            # Degree assortativity coefficient
            return nx.degree_assortativity_coefficient(graph)
        except:
            return 0.0

    def _compute_clustering_bias(self, graph: nx.Graph) -> float:
        """
        Compute clustering bias (local vs. global connectivity).

        Compares average clustering coefficient to density.
        High ratio = local clustering dominates (strong force-like).

        Args:
            graph: Adjacency graph

        Returns:
            Clustering bias ratio
        """
        if graph.number_of_nodes() == 0:
            return 0.0

        avg_clustering = nx.average_clustering(graph)
        density = nx.density(graph)

        if density > 0:
            return avg_clustering / density
        else:
            return 0.0

    def _compute_edge_asymmetry(self, prev_graph: nx.Graph, curr_graph: nx.Graph) -> Dict[str, float]:
        """
        Compute asymmetry in edge creation vs. destruction.

        Args:
            prev_graph: Graph at t-1
            curr_graph: Graph at t

        Returns:
            Dictionary with edge asymmetry metrics
        """
        prev_edges = set(prev_graph.edges())
        curr_edges = set(curr_graph.edges())

        edges_added = len(curr_edges - prev_edges)
        edges_removed = len(prev_edges - curr_edges)

        # Asymmetry ratio: (added - removed) / (added + removed)
        total = edges_added + edges_removed
        if total > 0:
            asymmetry_ratio = (edges_added - edges_removed) / total
        else:
            asymmetry_ratio = 0.0

        return {
            'edges_added': edges_added,
            'edges_removed': edges_removed,
            'asymmetry_ratio': asymmetry_ratio,
        }

    def _compute_spatial_correlation(self, graph: nx.Graph) -> float:
        """
        Compute spatial correlation (clustering of triangles).

        Measures how often neighbors of neighbors are also neighbors.

        Args:
            graph: Adjacency graph

        Returns:
            Spatial correlation coefficient
        """
        if graph.number_of_nodes() < 3:
            return 0.0

        # Transitivity = fraction of triads that are closed
        try:
            return nx.transitivity(graph)
        except:
            return 0.0

    def _compute_variance(self, history: list) -> float:
        """
        Compute variance of a historical series.

        Args:
            history: List of values

        Returns:
            Variance
        """
        if len(history) < 2:
            return 0.0

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        return variance
