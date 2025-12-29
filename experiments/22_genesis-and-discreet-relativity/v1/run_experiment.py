"""
Canonical Experiment Runner
============================

Experiment 22: Genesis and Discrete Relativity

Implements the canonical 15-X substrate update rule with full observer suite.

Update Rule Components:
- Expand: Neighbor-of-neighbor adjacency growth (causal spread)
- Mutate: Edge decay and rewiring (structural dynamics)
- Bias: Preferential attachment and triangle closure (emergent interactions)

All observers track derived quantities:
- Genesis, Relativity, PiDrift, Constants, Entropy, Particle, ForceCollapse
"""

import random
import math
from ..shared.substrate import SubstrateState, UpdateRule
from ..shared.experiment import (
    ExperimentConfig,
    run_experiment,
    create_simple_initial_state,
    create_ring_initial_state,
    create_star_initial_state,
    create_grid_initial_state,
    create_circle_initial_state,
)
from ..shared.observers import (
    GenesisObserver,
    RelativityObserver,
    PiDriftObserver,
    ConstantsDriftObserver,
    EntropyObserver,
    ParticleObserver,
    ForceCollapseObserver,
    WarpObserver,
    HorizonObserver
)


def spatial_distance(pos1, pos2):
    """Calculate Euclidean distance between two 3D positions."""
    return math.sqrt(
        (pos1[0] - pos2[0]) ** 2 +
        (pos1[1] - pos2[1]) ** 2 +
        (pos1[2] - pos2[2]) ** 2
    )


class ExpandingCircleRule(UpdateRule):
    """
    Expanding circle rule for π drift measurement.

    Entities start on a circle and expand radially outward with each tick.
    This simulates horizon growth in tick-frame cosmology.

    As radius increases, we measure π(t, R) to detect drift.
    """

    def __init__(self, expansion_rate: float = 0.01):
        """
        Initialize expanding circle rule.

        Args:
            expansion_rate: Radial expansion per tick (fraction of current radius)
        """
        self.expansion_rate = expansion_rate

    def expand(self, state: SubstrateState) -> SubstrateState:
        """
        Expand: Move all entities radially outward.

        Each entity moves away from origin proportional to its current distance.
        This simulates cosmic expansion / horizon growth.

        IMPORTANT: Positions are quantized to integer lattice points to simulate
        discrete spacetime. This introduces geometric discretization effects that
        can cause pi drift.
        """
        positions = state.positions

        for entity_id, pos in positions.items():
            x, y, z = pos

            # Calculate current distance from origin (in XY plane)
            r_current = math.sqrt(x ** 2 + y ** 2)

            if r_current > 0.01:  # Avoid division by zero
                # Expand radially outward
                expansion_factor = 1.0 + self.expansion_rate
                new_x = x * expansion_factor
                new_y = y * expansion_factor
                new_z = z  # Keep Z constant (we're in a 2D slice)

                # QUANTIZE TO INTEGER LATTICE POINTS
                # This creates discrete spacetime and introduces measurement drift
                new_x = round(new_x)
                new_y = round(new_y)
                new_z = round(new_z)

                positions[entity_id] = (float(new_x), float(new_y), float(new_z))

        return state

    def mutate(self, state: SubstrateState) -> SubstrateState:
        """No mutation - preserve circular geometry."""
        return state

    def bias(self, state: SubstrateState) -> SubstrateState:
        """No bias - preserve uniform distribution."""
        return state


class SpatialUpdateRule(UpdateRule):
    """
    Spatial update rule using geometric distance.

    This rule respects spatial embedding and uses geometric distance
    to determine adjacency changes. This allows for proper geometric
    π measurements in the PiDriftObserver.

    Components:
    - Expand: Connect entities within spatial distance threshold
    - Mutate: Decay edges and rewire to nearby entities
    - Bias: Preferential attachment weighted by spatial proximity
    """

    def __init__(
            self,
            connection_distance: float = 5.0,
            expand_prob: float = 0.1,
            decay_prob: float = 0.05,
            rewire_prob: float = 0.1,
            bias_strength: float = 0.05,
    ):
        """
        Initialize the spatial update rule.

        Args:
            connection_distance: Maximum distance for new connections
            expand_prob: Probability of connecting to nearby entities
            decay_prob: Probability of edge decay
            rewire_prob: Probability of edge rewiring
            bias_strength: Strength of spatial clustering bias
        """
        self.connection_distance = connection_distance
        self.expand_prob = expand_prob
        self.decay_prob = decay_prob
        self.rewire_prob = rewire_prob
        self.bias_strength = bias_strength

    def expand(self, state: SubstrateState) -> SubstrateState:
        """
        Expand: Connect entities within spatial distance.

        For each entity, find nearby entities (within connection_distance)
        that are not yet connected and connect with probability expand_prob.
        """
        graph = state.adjacency
        positions = state.positions
        new_edges = []

        # For each entity, find nearby entities to connect
        entities = list(state.entities.keys())
        for entity in entities:
            if entity not in positions:
                continue

            pos1 = positions[entity]

            # Find nearby entities
            for other in entities:
                if other == entity or other not in positions:
                    continue
                if graph.has_edge(entity, other):
                    continue

                pos2 = positions[other]
                dist = spatial_distance(pos1, pos2)

                # Connect if within distance and probability check passes
                if dist <= self.connection_distance:
                    if random.random() < self.expand_prob:
                        new_edges.append((entity, other))

        # Add new edges
        for u, v in new_edges:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        return state

    def mutate(self, state: SubstrateState) -> SubstrateState:
        """
        Mutate: Decay and spatial rewiring.

        Edges decay randomly, and can be rewired to nearby entities.
        """
        graph = state.adjacency
        positions = state.positions
        edges_to_remove = []
        edges_to_add = []

        # Process each edge
        for u, v in list(graph.edges()):
            # Decay: remove edge
            if random.random() < self.decay_prob:
                edges_to_remove.append((u, v))
                continue

            # Rewire: move edge to nearby entity
            if random.random() < self.rewire_prob:
                if u in positions and v in positions:
                    # Find entities near v
                    nearby = []
                    pos_v = positions[v]
                    for entity in state.entities.keys():
                        if entity == u or entity not in positions:
                            continue
                        if graph.has_edge(u, entity):
                            continue
                        dist = spatial_distance(positions[entity], pos_v)
                        if dist <= self.connection_distance:
                            nearby.append(entity)

                    if nearby:
                        new_target = random.choice(nearby)
                        edges_to_remove.append((u, v))
                        edges_to_add.append((u, new_target))

        # Apply mutations
        for u, v in edges_to_remove:
            if graph.has_edge(u, v):
                graph.remove_edge(u, v)

        for u, v in edges_to_add:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        return state

    def bias(self, state: SubstrateState) -> SubstrateState:
        """
        Bias: Spatial clustering tendency.

        Entities in dense regions have higher probability of connecting.
        """
        graph = state.adjacency
        positions = state.positions
        new_edges = []

        entities = list(state.entities.keys())

        # Spatial clustering: connect entities in dense neighborhoods
        for entity in entities:
            if entity not in positions:
                continue

            if random.random() > self.bias_strength:
                continue

            pos1 = positions[entity]

            # Find closest non-connected entity
            closest = None
            min_dist = float('inf')

            for other in entities:
                if other == entity or other not in positions:
                    continue
                if graph.has_edge(entity, other):
                    continue

                dist = spatial_distance(pos1, positions[other])
                if dist < min_dist and dist <= self.connection_distance * 1.5:
                    min_dist = dist
                    closest = other

            if closest is not None:
                new_edges.append((entity, closest))

        # Apply bias edges
        for u, v in new_edges:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        return state


class CanonicalUpdateRule(UpdateRule):
    """
    Canonical 15-X Substrate Update Rule with Unseen-Age Energy Model.

    The universe accumulates "unseen energy" until the first observer attaches.
    After attachment, this energy decays over time and drives all dynamics.

    Components:
    - Expand: adjacency growth
    - Mutate: decay and rewiring
    - Bias: preferential attachment + triangle closure
    - Birth: new entity creation

    All probabilities become functions of:
        - T_unseen: ticks before first observation
        - t_obs: ticks since first observation
    """

    def __init__(
            self,
            base_expand: float = 0.3,
            base_decay: float = 0.05,
            base_rewire: float = 0.1,
            base_bias: float = 0.2,
            base_birth: float = 0.02,
            k_energy: float = 0.01,
            k_cooling: float = 0.005,
    ):
        """
        Initialize the canonical update rule.

        Args:
            base_expand: baseline expand probability
            base_decay: baseline decay probability
            base_rewire: baseline rewiring probability
            base_bias: baseline bias strength
            base_birth: baseline birth probability
            k_energy: scaling factor for initial energy
            k_cooling: scaling factor for cooling timescale
        """
        self.base_expand = base_expand
        self.base_decay = base_decay
        self.base_rewire = base_rewire
        self.base_bias = base_bias
        self.base_birth = base_birth

        # Energy model parameters
        self.k_energy = k_energy
        self.k_cooling = k_cooling

        # Set by the engine when the first observer attaches
        self.T_unseen = None
        self.t_obs = 0

    # ---------------------------------------------------------
    #  ENERGY MODEL
    # ---------------------------------------------------------

    def set_unseen_age(self, T_unseen: int):
        """Called by the engine when the first observer attaches."""
        self.T_unseen = T_unseen
        self.t_obs = 0

        # Initial energy and cooling timescale
        self.E0 = self.k_energy * T_unseen
        self.tau = max(1.0, self.k_cooling * T_unseen)

    def tick(self):
        """Called once per tick AFTER observation."""
        if self.T_unseen is not None:
            self.t_obs += 1

    def energy(self) -> float:
        """Energy decays exponentially after observation."""
        if self.T_unseen is None:
            # Universe still unseen → accumulating energy
            return 0.0
        return self.E0 * math.exp(-self.t_obs / self.tau)

    # ---------------------------------------------------------
    #  PROBABILITY FUNCTIONS
    # ---------------------------------------------------------

    def expand_prob(self):
        E = self.energy()
        return self.base_expand * (1 + E)

    def decay_prob(self):
        E = self.energy()
        # decay increases as energy falls
        return self.base_decay * (1 + (1 / (1 + E)))

    def rewire_prob(self):
        E = self.energy()
        return self.base_rewire * (1 + 0.5 * E)

    def bias_strength(self):
        E = self.energy()
        return self.base_bias * (1 + E)

    def birth_prob(self):
        E = self.energy()
        return self.base_birth * (1 + E)

    # ---------------------------------------------------------
    #  UPDATE RULES
    # ---------------------------------------------------------

    def expand(self, state: SubstrateState) -> SubstrateState:
        graph = state.adjacency
        new_edges = []
        p_expand = self.expand_prob()

        for node in list(graph.nodes()):
            neighbors = list(graph.neighbors(node))
            for neighbor in neighbors:
                for second_neighbor in graph.neighbors(neighbor):
                    if second_neighbor == node:
                        continue
                    if graph.has_edge(node, second_neighbor):
                        continue
                    if random.random() < p_expand:
                        new_edges.append((node, second_neighbor))

        for u, v in new_edges:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        # Birth
        if random.random() < self.birth_prob() and state.entities:
            positions = state.positions
            parent = random.choice(list(state.entities.keys()))
            px, py, pz = positions[parent]

            new_id = max(state.entities.keys()) + 1
            nx = px + random.uniform(-1, 1)
            ny = py + random.uniform(-1, 1)
            nz = pz

            state.entities[new_id] = {}
            state.positions[new_id] = (nx, ny, nz)
            graph.add_node(new_id)
            graph.add_edge(parent, new_id)

        return state

    def mutate(self, state: SubstrateState) -> SubstrateState:
        graph = state.adjacency
        edges_to_remove = []
        edges_to_add = []

        p_decay = self.decay_prob()
        p_rewire = self.rewire_prob()

        for u, v in list(graph.edges()):
            if random.random() < p_decay:
                edges_to_remove.append((u, v))
                continue

            if random.random() < p_rewire:
                v_neighbors = list(graph.neighbors(v))
                if v_neighbors:
                    new_target = random.choice(v_neighbors)
                    if new_target != u and not graph.has_edge(u, new_target):
                        edges_to_remove.append((u, v))
                        edges_to_add.append((u, new_target))

        for u, v in edges_to_remove:
            if graph.has_edge(u, v):
                graph.remove_edge(u, v)

        for u, v in edges_to_add:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        return state

    def bias(self, state: SubstrateState) -> SubstrateState:
        graph = state.adjacency
        new_edges = []
        p_bias = self.bias_strength()

        # Preferential attachment
        if graph.number_of_nodes() > 1:
            degrees = dict(graph.degree())
            nodes = list(graph.nodes())
            weights = [degrees[n] + 1 for n in nodes]

            for _ in range(max(1, int(len(nodes) * p_bias))):
                source = random.choices(nodes, weights=weights, k=1)[0]
                target = random.choices(nodes, weights=weights, k=1)[0]
                if source != target and not graph.has_edge(source, target):
                    new_edges.append((source, target))

        # Triangle closure
        for node in list(graph.nodes()):
            neighbors = list(graph.neighbors(node))
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i + 1:]:
                    if not graph.has_edge(n1, n2):
                        if random.random() < p_bias:
                            new_edges.append((n1, n2))

        for u, v in new_edges:
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)

        return state


def main():
    """Run the spatial tick-frame experiment with geometric π measurement."""

    # Configuration
    OUTPUT_DIR = "results"
    MAX_TICKS = 1000  # Just a few ticks to validate π measurement
    LOG_INTERVAL = 1  # Log every tick
    NUM_POINTS = 1000  # Points on the circle
    CIRCLE_RADIUS = 10.0  # Circle radius

    # Create expanding circle rule to measure pi drift during expansion
    update_rule = ExpandingCircleRule(
        expansion_rate=0.01  # 1% radial expansion per tick
    )

    # Create observers
    # Circle expands by 1% per tick: R(t) = R0 * (1.01)^t
    # After 1000 ticks: R(1000) ≈ 10 * (1.01)^1000 ≈ 209,591
    max_radius = 250000  # Track all radii up to final expansion
    observers = [
        #        PiDriftObserver(max_radius=max_radius, log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
        GenesisObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        RelativityObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        ConstantsDriftObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        EntropyObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        ParticleObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        ForceCollapseObserver(log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        HorizonObserver(root_id=0, max_depth=8, log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
#        WarpObserver(warp_center_id=0, strength=0.2, log_interval=LOG_INTERVAL, output_dir=OUTPUT_DIR),
    ]

    # Create experiment configuration
    config = ExperimentConfig(
        name="Experiment 22 - Pi Drift (Discrete Spacetime)",
        description=(
            "Expanding circle with DISCRETE LATTICE QUANTIZATION.\n"
            f"{NUM_POINTS} entities start on circle of radius {CIRCLE_RADIUS}.\n"
            "Positions quantized to integers. Measuring pi(t, R) drift from discretization."
        ),
        initial_state_builder=lambda: create_circle_initial_state(
            num_points=NUM_POINTS,
            radius=CIRCLE_RADIUS
        ),
        update_rule=update_rule,
        observers=observers,
        max_ticks=MAX_TICKS,
    )

    # Run experiment
    engine = run_experiment(config, verbose=True)

    print(f"\nOutput files written to: {OUTPUT_DIR}")
    print(f"Check the CSV files for observer data.")
    print(f"\nFinal substrate state:")
    print(f"  - Entities: {len(engine.state.entities)}")
    print(f"  - Edges: {engine.state.adjacency.number_of_edges()}")
    print(
        f"  - Avg degree: {sum(d for _, d in engine.state.adjacency.degree()) / max(1, len(engine.state.entities)):.2f}")


if __name__ == "__main__":
    main()
