"""
Genesis Experiment - Adjacency Graph Growth
============================================

Tests the genesis observer with the canonical update rule that actually
modifies the adjacency graph through expand/mutate/bias operations.

This should show:
- Growing horizon radius over time
- Expanding frontier
- Increasing entity and edge counts
- Non-trivial branching factors
"""

import random
from ..shared.substrate import SubstrateState
from ..shared.experiment import (
    ExperimentConfig,
    run_experiment,
    create_simple_initial_state,
)
from ..shared.observers import GenesisObserver
from run_experiment import CanonicalUpdateRule


def main():
    """Run a genesis experiment with graph growth dynamics."""

    OUTPUT_DIR = "results"
    MAX_TICKS = 100000  # Very long run to see long-term dynamics
    LOG_INTERVAL = 100  # Log every 100 ticks to keep output manageable

    # PARAMETER PRESETS - Try different growth regimes
    # NOTE: CanonicalUpdateRule now uses "Unseen-Age Energy Model"
    # Parameters are: base_expand, base_decay, base_rewire, base_bias, base_birth

    # 1. EXPLOSIVE GROWTH (original)
    # explosive = dict(base_expand=0.3, base_decay=0.05, base_rewire=0.1,
    #                  base_bias=0.2, base_birth=0.3)

    # 2. BALANCED GROWTH (moderate decay to slow edge growth)
    # balanced = dict(base_expand=0.2, base_decay=0.15, base_rewire=0.1,
    #                 base_bias=0.15, base_birth=0.15)

    # 3. SPARSE GROWTH (high decay, low birth - sparse networks)
    sparse = dict(base_expand=0.2, base_decay=0.25, base_rewire=0.15,
                  base_bias=0.1, base_birth=0.1)

    # 4. SLOW & STEADY (very gradual growth)
    # slow = dict(base_expand=0.15, base_decay=0.2, base_rewire=0.1,
    #             base_bias=0.1, base_birth=0.05)

    # Select configuration
    config_params = sparse

    # Canonical update rule - with Unseen-Age Energy Model!
    # Energy will be 0 until first observer attaches, then decay exponentially
    update_rule = CanonicalUpdateRule(**config_params)

    # Genesis observer
    observers = [
        GenesisObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
    ]

    # Start with a SMALL initial state - just a few connected entities
    # This way we can see the graph grow from genesis
    def create_genesis_seed():
        """Create minimal seed state - 3 entities in a triangle."""
        state = SubstrateState()

        # Create 3 entities
        for i in range(3):
            state.entities[i] = {}
            state.positions[i] = (float(i), 0.0, 0.0)
            state.adjacency.add_node(i)

        # Connect them in a triangle
        state.adjacency.add_edge(0, 1)
        state.adjacency.add_edge(1, 2)
        state.adjacency.add_edge(2, 0)

        return state

    # Create experiment
    config_name = "SPARSE GROWTH"  # Update this to match selected config
    config = ExperimentConfig(
        name=f"Experiment 22 - Genesis ({config_name})",
        description=(
            f"Graph genesis from minimal seed state (3 entities).\n"
            f"Configuration: {config_name}\n"
            f"Unseen-Age Energy Model: dynamics scale with observation history.\n"
            f"Base parameters: expand={config_params['base_expand']}, "
            f"decay={config_params['base_decay']}, birth={config_params['base_birth']}\n"
            f"Observing horizon growth, frontier expansion, and entity population."
        ),
        initial_state_builder=create_genesis_seed,
        update_rule=update_rule,
        observers=observers,
        max_ticks=MAX_TICKS,
    )

    # Run experiment
    print("=" * 80)
    print(f"GENESIS EXPERIMENT - {config_name}")
    print("=" * 80)
    print(f"Initial state: 3 entities in triangle")
    print(f"Update rule: Canonical (expand + mutate + bias + birth)")
    print(f"")
    print(f"Base Parameters (scale with unseen-age energy):")
    print(f"  - base_birth:    {config_params['base_birth']:.2f} (entity creation)")
    print(f"  - base_expand:   {config_params['base_expand']:.2f} (neighbor-of-neighbor connections)")
    print(f"  - base_decay:    {config_params['base_decay']:.2f} (edge removal)")
    print(f"  - base_rewire:   {config_params['base_rewire']:.2f} (edge rewiring)")
    print(f"  - base_bias:     {config_params['base_bias']:.2f} (preferential attachment)")
    print(f"")
    print(f"Energy Model: E(t) = E0 * exp(-t/tau) after first observation")
    print(f"")
    print(f"Max ticks: {MAX_TICKS}")
    print("=" * 80)
    print()

    engine = run_experiment(config, verbose=True)

    print(f"\n{'=' * 70}")
    print("FINAL STATE:")
    print(f"  - Entities: {len(engine.state.entities)} (started with 3)")
    print(f"  - Edges: {engine.state.adjacency.number_of_edges()} (started with 3)")
    avg_degree = sum(d for _, d in engine.state.adjacency.degree()) / max(1, len(engine.state.entities))
    print(f"  - Avg degree: {avg_degree:.2f}")
    print(f"  - Output: {OUTPUT_DIR}/genesis_metrics.csv")
    print("=" * 70)


if __name__ == "__main__":
    main()
