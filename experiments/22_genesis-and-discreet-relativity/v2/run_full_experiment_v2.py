"""
Full Experiment v2 - All Observers (except Pi Drift)
=====================================================

Comprehensive experiment runner with:
- All observers: genesis, constants_drift, relativity, entropy, particle,
  force_collapse, horizon, warp
- Configurable pre-observation period (T_unseen)
- Energy model presets (cold, warm, hot universe)

This allows testing the hypothesis that physical constants emerge from
substrate dynamics and vary with the "age" of the universe before observation.
"""

import random

from run_experiment import CanonicalUpdateRule
from ..shared.experiment import (
    ExperimentConfig,
    run_experiment,
)
from ..shared.observers import (
    GenesisObserver,
    ConstantsDriftObserver,
    RelativityObserver,
    EntropyObserver,
    ParticleObserver,
    ForceCollapseObserver,
    HorizonObserver,
    WarpObserver,
)
from ..shared.substrate import SubstrateState


def create_small_world_network(n=20, k=4, rewire_prob=0.1):
    """
    Create Watts-Strogatz small-world network.

    Args:
        n: Number of entities
        k: Each node connects to k nearest neighbors in ring
        rewire_prob: Probability of rewiring each edge

    Returns:
        SubstrateState with small-world topology
    """
    state = SubstrateState()

    # Create nodes in ring layout
    for i in range(n):
        state.entities[i] = {}
        # Position in circle
        angle = 2 * 3.14159 * i / n
        radius = 10.0
        x = radius * (angle if angle < 3.14159 else -(2 * 3.14159 - angle))
        y = radius * (angle if angle < 3.14159 else (2 * 3.14159 - angle))
        state.positions[i] = (x, y, 0.0)
        state.adjacency.add_node(i)

    # Create ring lattice
    for i in range(n):
        for j in range(1, k // 2 + 1):
            neighbor = (i + j) % n
            state.adjacency.add_edge(i, neighbor)

    # Rewire edges
    edges = list(state.adjacency.edges())
    for u, v in edges:
        if random.random() < rewire_prob:
            state.adjacency.remove_edge(u, v)
            # Pick random target (not self, not already connected)
            candidates = [i for i in range(n) if i != u and not state.adjacency.has_edge(u, i)]
            if candidates:
                new_target = random.choice(candidates)
                state.adjacency.add_edge(u, new_target)

    return state


def main():
    """Run comprehensive experiment with all observers."""

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    OUTPUT_DIR = "results"
    MAX_TICKS = 10000
    LOG_INTERVAL = 10

    # ========================================================================
    # ENERGY MODEL PRESETS
    # ========================================================================

    # COLD START - Immediate observation (T_unseen = 0)
    # Result: Low energy throughout, stable constants, slow growth
    cold_start = {
        'T_unseen': 0,
        'k_energy': 0.01,
        'k_cooling': 0.005,
        'description': 'Observer present from beginning (cold universe)'
    }

    # WARM START - Moderate pre-observation period
    # Result: Initial energy boost, then gradual cooling
    warm_start = {
        'T_unseen': 1000,
        'k_energy': 1.0,
        'k_cooling': 0.01,
        'description': '1000 ticks before observation (warm universe)'
    }

    # HOT START - Long pre-observation period with high energy
    # Result: Explosive initial dynamics, slow cooling
    hot_start = {
        'T_unseen': 5000,
        'k_energy': 5.0,
        'k_cooling': 0.001,
        'description': '5000 ticks before observation (hot universe)'
    }

    # EXTREME - Very long pre-observation, extreme energy
    # Result: Chaotic early phase, dramatic constant drift
    extreme_start = {
        'T_unseen': 10000,
        'k_energy': 10.0,
        'k_cooling': 0.0005,
        'description': '10000 ticks before observation (extremely hot universe)'
    }

    # ========================================================================
    # SELECT CONFIGURATION
    # ========================================================================

    # Choose one:
    energy_config = warm_start
    config_name = "WARM START"

    # ========================================================================
    # UPDATE RULE PARAMETERS
    # ========================================================================

    # Base dynamics (before energy scaling)
    base_params = {
        'base_birth': 0.05,
        'base_expand': 0.15,
        'base_decay': 0.15,
        'base_rewire': 0.10,
        'base_bias': 0.10,
    }

    # Combine with energy model
    update_params = {**base_params,
                     'k_energy': energy_config['k_energy'],
                     'k_cooling': energy_config['k_cooling']}

    # Create update rule
    update_rule = CanonicalUpdateRule(**update_params)

    # Set pre-observation age (this is the key parameter!)
    update_rule.set_unseen_age(energy_config['T_unseen'])

    # Calculate initial energy
    if energy_config['T_unseen'] > 0:
        E0 = energy_config['k_energy'] * energy_config['T_unseen']
        tau = max(1.0, energy_config['k_cooling'] * energy_config['T_unseen'])
        print(f"\nEnergy Model Initialized:")
        print(f"  E0 = {E0:.2f} (initial energy)")
        print(f"  tau = {tau:.2f} (cooling timescale)")
        print(f"  Energy at tick 1: {E0:.2f}")
        print(f"  Energy at tick 100: {E0 * 2.718 ** (-100 / tau):.2f}")
        print(f"  Energy at tick {MAX_TICKS}: {E0 * 2.718 ** (-MAX_TICKS / tau):.4f}")
    else:
        print(f"\nEnergy Model: COLD START (E = 0 throughout)")

    # ========================================================================
    # OBSERVERS
    # ========================================================================

    observers = [
        GenesisObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        ConstantsDriftObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        RelativityObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        EntropyObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        ParticleObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        ForceCollapseObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        HorizonObserver(root_id=0, max_depth=10, log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        WarpObserver(warp_center_id=0, strength=0.5, log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
    ]

    # ========================================================================
    # INITIAL STATE
    # ========================================================================

    initial_state = create_small_world_network(n=20, k=4, rewire_prob=0.1)

    # ========================================================================
    # EXPERIMENT CONFIGURATION
    # ========================================================================

    config = ExperimentConfig(
        name=f"Experiment 22 v2 - Full Observatory ({config_name})",
        description=(
            f"Comprehensive observation of substrate dynamics.\n"
            f"\n"
            f"Energy Configuration: {config_name}\n"
            f"  {energy_config['description']}\n"
            f"  T_unseen: {energy_config['T_unseen']} ticks\n"
            f"  k_energy: {energy_config['k_energy']}\n"
            f"  k_cooling: {energy_config['k_cooling']}\n"
            f"\n"
            f"Base Dynamics:\n"
            f"  birth: {base_params['base_birth']}\n"
            f"  expand: {base_params['base_expand']}\n"
            f"  decay: {base_params['base_decay']}\n"
            f"  rewire: {base_params['base_rewire']}\n"
            f"  bias: {base_params['base_bias']}\n"
            f"\n"
            f"Observers:\n"
            f"  - Genesis (entities, edges, horizon, branching)\n"
            f"  - Constants Drift (alpha, G, h, Lambda)\n"
            f"  - Relativity (time dilation, velocity effects)\n"
            f"  - Entropy (graph disorder)\n"
            f"  - Particle (collision dynamics)\n"
            f"  - Force Collapse (clustering forces)\n"
            f"  - Horizon (causal boundaries)\n"
            f"  - Warp (spacetime curvature)"
        ),
        initial_state_builder=lambda: initial_state,
        update_rule=update_rule,
        observers=observers,
        max_ticks=MAX_TICKS,
    )

    # ========================================================================
    # RUN EXPERIMENT
    # ========================================================================

    print("=" * 80)
    print(f"FULL EXPERIMENT v2 - {config_name}")
    print("=" * 80)
    print(f"Initial state: 20 entities (small-world network)")
    print(f"Update rule: Canonical with Unseen-Age Energy Model")
    print(f"Pre-observation period: {energy_config['T_unseen']} ticks")
    print(f"")
    print(f"Active Observers: {len(observers)}")
    for obs in observers:
        print(f"  - {obs.name}")
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
    print(f"")
    print(f"Output files in: {OUTPUT_DIR}/")
    print(f"  - genesis_metrics.csv")
    print(f"  - constants_drift.csv")
    print(f"  - relativity_metrics.csv")
    print(f"  - entropy_metrics.csv")
    print(f"  - particle_metrics.csv")
    print(f"  - force_collapse_metrics.csv")
    print(f"  - horizon_metrics.csv")
    print(f"  - warp_metrics.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()
