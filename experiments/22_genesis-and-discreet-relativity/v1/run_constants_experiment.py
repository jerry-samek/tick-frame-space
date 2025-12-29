"""
Constants Drift Experiment
===========================

Tracks the evolution of emergent physical "constants" over time:
- α(t): Fine structure constant proxy (clustering coefficient)
- G(t): Gravitational constant proxy (transitivity)
- h(t): Planck constant proxy (minimum degree)
- Λ(t): Cosmological constant proxy (expansion rate)

Tests whether these constants remain stable or drift as the substrate evolves.
"""

import random
from ..shared.substrate import SubstrateState
from ..shared.experiment import (
    ExperimentConfig,
    run_experiment,
)
from ..shared.observers import ConstantsDriftObserver
from run_experiment import CanonicalUpdateRule


def main():
    """Run constants drift experiment with graph dynamics."""

    OUTPUT_DIR = "results"
    MAX_TICKS = 10000  # Long run to see constant evolution
    LOG_INTERVAL = 10  # Log every 10 ticks

    # PARAMETER PRESETS - Different dynamics regimes

    # 1. STABLE GROWTH (constants should stabilize)
    stable = dict(base_expand=0.15, base_decay=0.15, base_rewire=0.1,
                  base_bias=0.1, base_birth=0.05,
                  k_energy=0.5, k_cooling=0.01)

    # 2. CHAOTIC GROWTH (constants should drift)
    # chaotic = dict(base_expand=0.3, base_decay=0.2, base_rewire=0.25,
    #                base_bias=0.15, base_birth=0.15,
    #                k_energy=1.0, k_cooling=0.001)

    # 3. SLOW EVOLUTION (minimal drift expected)
    # slow = dict(base_expand=0.1, base_decay=0.1, base_rewire=0.05,
    #             base_bias=0.05, base_birth=0.02,
    #             k_energy=0.1, k_cooling=0.05)

    # Select configuration
    config_params = stable
    config_name = "STABLE GROWTH"

    # Create update rule
    update_rule = CanonicalUpdateRule(**config_params)

    # Observers
    observers = [
        ConstantsDriftObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
    ]

    # Initial state: Start with a moderate network (not too small)
    def create_initial_network():
        """Create initial network with ~20 entities in small-world topology."""
        state = SubstrateState()

        n = 20  # Initial entities
        k = 4   # Each node connects to k nearest neighbors

        # Create nodes
        for i in range(n):
            state.entities[i] = {}
            # Arrange in circle
            angle = 2 * 3.14159 * i / n
            x = 10.0 * (1 + 0.5 * (i / n))  # Spiral outward slightly
            y = 10.0 * (1 + 0.5 * (i / n))
            state.positions[i] = (x * angle, y * angle, 0.0)
            state.adjacency.add_node(i)

        # Create ring lattice (each connects to k nearest neighbors)
        for i in range(n):
            for j in range(1, k // 2 + 1):
                neighbor = (i + j) % n
                state.adjacency.add_edge(i, neighbor)

        # Rewire with small probability (Watts-Strogatz small-world)
        rewire_prob = 0.1
        edges = list(state.adjacency.edges())
        for u, v in edges:
            if random.random() < rewire_prob:
                state.adjacency.remove_edge(u, v)
                # Pick random target
                new_target = random.choice([i for i in range(n) if i != u])
                if not state.adjacency.has_edge(u, new_target):
                    state.adjacency.add_edge(u, new_target)

        return state

    # Create experiment
    config = ExperimentConfig(
        name=f"Experiment 22 - Constants Drift ({config_name})",
        description=(
            f"Tracking emergent physical constants over {MAX_TICKS} ticks.\n"
            f"Configuration: {config_name}\n"
            f"Unseen-Age Energy Model with parameters:\n"
            f"  expand={config_params['base_expand']}, "
            f"decay={config_params['base_decay']}, birth={config_params['base_birth']}\n"
            f"  k_energy={config_params['k_energy']}, k_cooling={config_params['k_cooling']}\n"
            f"\n"
            f"Constants tracked:\n"
            f"  - alpha(t): Fine structure (avg clustering)\n"
            f"  - G(t): Gravitational clustering (transitivity)\n"
            f"  - h(t): Planck quantum (min degree)\n"
            f"  - Lambda(t): Cosmological expansion (growth rate)"
        ),
        initial_state_builder=create_initial_network,
        update_rule=update_rule,
        observers=observers,
        max_ticks=MAX_TICKS,
    )

    # Run experiment
    print("=" * 80)
    print(f"CONSTANTS DRIFT EXPERIMENT - {config_name}")
    print("=" * 80)
    print(f"Initial state: 20 entities in small-world network")
    print(f"Update rule: Canonical with Unseen-Age Energy Model")
    print(f"")
    print(f"Base Parameters:")
    print(f"  - base_birth:    {config_params['base_birth']:.2f}")
    print(f"  - base_expand:   {config_params['base_expand']:.2f}")
    print(f"  - base_decay:    {config_params['base_decay']:.2f}")
    print(f"  - base_rewire:   {config_params['base_rewire']:.2f}")
    print(f"  - base_bias:     {config_params['base_bias']:.2f}")
    print(f"")
    print(f"Energy Model:")
    print(f"  - k_energy:      {config_params['k_energy']:.2f} (initial energy scaling)")
    print(f"  - k_cooling:     {config_params['k_cooling']:.3f} (decay timescale)")
    print(f"")
    print(f"Max ticks: {MAX_TICKS}")
    print(f"Log interval: {LOG_INTERVAL}")
    print("=" * 80)
    print()

    engine = run_experiment(config, verbose=True)

    print(f"\n{'=' * 80}")
    print("FINAL STATE:")
    print(f"  - Entities: {len(engine.state.entities)} (started with 20)")
    print(f"  - Edges: {engine.state.adjacency.number_of_edges()}")
    avg_degree = sum(d for _, d in engine.state.adjacency.degree()) / max(1, len(engine.state.entities))
    print(f"  - Avg degree: {avg_degree:.2f}")
    print(f"  - Output: {OUTPUT_DIR}/constants_drift.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()
