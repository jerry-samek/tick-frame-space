"""
Constants Drift Observer
========================

Tracks emergent physical constants over time: α(t), G(t), h(t), Λ(t).

In tick-frame physics, constants may emerge from substrate dynamics:
- α(t): Fine structure constant (coupling strength)
- G(t): Gravitational constant (clustering tendency)
- h(t): Planck constant (quantum of action)
- Λ(t): Cosmological constant (expansion rate)

These are proxied by graph properties that capture similar dynamics.
"""

from typing import Optional
import networkx as nx
from .base import Observer


class ConstantsDriftObserver(Observer):
    """
    Observer for emergent physical constants.

    Tracks:
    - α(t): Coupling strength (average edge weight / clustering coefficient)
    - G(t): Gravitational clustering (global clustering coefficient)
    - h(t): Minimal action (minimum degree)
    - Λ(t): Expansion rate (growth rate of entity count)
    """

    def __init__(self, log_interval: int = 10, output_dir: Optional[str] = None):
        """
        Initialize ConstantsDriftObserver.

        Args:
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        super().__init__(name="ConstantsDrift", log_interval=log_interval, output_dir=output_dir)

        # Track constants over time
        self.memory['alpha_history'] = []
        self.memory['G_history'] = []
        self.memory['h_history'] = []
        self.memory['Lambda_history'] = []
        self.memory['previous_entity_count'] = 0

    def on_post_tick(self, state) -> None:
        """
        Compute emergent constants after each tick.

        Args:
            state: Current substrate state
        """
        tick = state.tick
        graph = state.adjacency
        num_entities = len(state.entities)

        # α(t): Fine structure constant proxy
        # Use clustering coefficient as a proxy for interaction strength
        if graph.number_of_nodes() > 0:
            alpha = nx.average_clustering(graph)
        else:
            alpha = 0.0

        # G(t): Gravitational constant proxy
        # Use global clustering coefficient (triangles / triads)
        if graph.number_of_nodes() > 2:
            try:
                G = nx.transitivity(graph)
            except:
                G = 0.0
        else:
            G = 0.0

        # h(t): Planck constant proxy
        # Use minimum degree as quantum of action
        if graph.number_of_nodes() > 0:
            degrees = [d for n, d in graph.degree()]
            h = min(degrees) if degrees else 0
        else:
            h = 0

        # Λ(t): Cosmological constant proxy
        # Use entity growth rate as expansion rate
        if self.memory['previous_entity_count'] > 0:
            Lambda = (num_entities - self.memory['previous_entity_count']) / self.memory['previous_entity_count']
        else:
            Lambda = 0.0

        # Update memory
        self.memory['alpha_history'].append(alpha)
        self.memory['G_history'].append(G)
        self.memory['h_history'].append(h)
        self.memory['Lambda_history'].append(Lambda)
        self.memory['previous_entity_count'] = num_entities

        # Compute drift (variance over time)
        alpha_drift = self._compute_variance(self.memory['alpha_history'])
        G_drift = self._compute_variance(self.memory['G_history'])
        h_drift = self._compute_variance(self.memory['h_history'])
        Lambda_drift = self._compute_variance(self.memory['Lambda_history'])

        # Log if needed
        if self.should_log(tick):
            data = {
                'tick': tick,
                'alpha': alpha,
                'G': G,
                'h': h,
                'Lambda': Lambda,
                'alpha_drift': alpha_drift,
                'G_drift': G_drift,
                'h_drift': h_drift,
                'Lambda_drift': Lambda_drift,
            }

            self.log_csv('constants_drift.csv', data)

            # Log summary
            summary = (
                f"[Constants t={tick}] "
                f"α={alpha:.4f} (drift={alpha_drift:.6f}), "
                f"G={G:.4f} (drift={G_drift:.6f}), "
                f"h={h}, "
                f"Λ={Lambda:.4f} (drift={Lambda_drift:.6f})\n"
            )
            self.log_text('constants_drift_log.txt', summary)

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
