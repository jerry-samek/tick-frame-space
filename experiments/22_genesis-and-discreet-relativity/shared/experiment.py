"""
Experiment Configuration and Runner
====================================

Provides configuration and execution infrastructure for tick-frame experiments.
"""

from typing import List, Callable, Optional
from dataclasses import dataclass
import time
from substrate import SubstrateState, UpdateRule, SubstrateEngine
from observers.base import Observer


@dataclass
class ExperimentConfig:
    """
    Configuration for a tick-frame experiment.

    Experiments are configurations, not separate engines.
    This class bundles together:
    - Initial state builder
    - Update rule
    - Observers
    - Execution parameters
    """
    name: str
    initial_state_builder: Callable[[], SubstrateState]
    update_rule: UpdateRule
    observers: List[Observer]
    max_ticks: int
    description: Optional[str] = None

    def __post_init__(self):
        """Validate configuration."""
        if self.max_ticks <= 0:
            raise ValueError("max_ticks must be positive")
        if not self.observers:
            raise ValueError("At least one observer must be provided")


def run_experiment(config: ExperimentConfig, verbose: bool = True) -> SubstrateEngine:
    """
    Run a configured experiment.

    Steps:
    1. Build initial state using the provided builder
    2. Create substrate engine
    3. Attach all observers
    4. Run for max_ticks
    5. Return the engine (with final state and observers)

    Args:
        config: Experiment configuration
        verbose: Whether to print progress

    Returns:
        The substrate engine after execution (contains final state and observers)
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running Experiment: {config.name}")
        print(f"{'='*60}")
        if config.description:
            print(f"{config.description}")
            print(f"{'-'*60}")

    # Build initial state
    if verbose:
        print(f"Building initial state...")
    initial_state = config.initial_state_builder()

    # Create engine
    if verbose:
        print(f"Creating substrate engine...")
        print(f"  - Entities: {len(initial_state.entities)}")
        print(f"  - Edges: {initial_state.adjacency.number_of_edges()}")
        print(f"  - Update rule: {config.update_rule.__class__.__name__}")

    engine = SubstrateEngine(initial_state, config.update_rule)

    # Attach observers
    if verbose:
        print(f"Attaching {len(config.observers)} observers:")
    for observer in config.observers:
        engine.add_observer(observer)
        if verbose:
            print(f"  - {observer.name}")

    # Run simulation
    if verbose:
        print(f"\n{'-'*60}")
        print(f"Running simulation for {config.max_ticks} ticks...")
        print(f"{'-'*60}")

    start_time = time.time()

    try:
        engine.run(config.max_ticks)
    except KeyboardInterrupt:
        if verbose:
            print(f"\n\nSimulation interrupted by user at tick {engine.state.tick}")
    except Exception as e:
        if verbose:
            print(f"\n\nSimulation failed at tick {engine.state.tick}: {e}")
        raise

    elapsed_time = time.time() - start_time

    # Print summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"Simulation Complete")
        print(f"{'='*60}")
        print(f"Final tick: {engine.state.tick}")
        print(f"Final entities: {len(engine.state.entities)}")
        print(f"Final edges: {engine.state.adjacency.number_of_edges()}")
        print(f"Elapsed time: {elapsed_time:.2f}s")
        print(f"Ticks/second: {engine.state.tick / elapsed_time:.2f}")
        print(f"{'='*60}\n")

    return engine


def create_simple_initial_state(num_entities: int = 10, num_edges: int = 15, spatial_size: float = None) -> SubstrateState:
    """
    Create a simple initial state with random spatial positions and connectivity.

    Args:
        num_entities: Number of initial entities
        num_edges: Number of initial edges
        spatial_size: Size of the spatial cube (default: scale with sqrt(num_entities))

    Returns:
        Initial substrate state with spatial embedding
    """
    import networkx as nx
    import random
    import math

    state = SubstrateState()

    # Determine spatial size (cube side length)
    if spatial_size is None:
        spatial_size = math.sqrt(num_entities) * 2.0

    # Create entities with random spatial positions
    for i in range(num_entities):
        state.entities[i] = {}
        # Random position in 3D cube [0, spatial_size]^3
        state.positions[i] = (
            random.uniform(0, spatial_size),
            random.uniform(0, spatial_size),
            random.uniform(0, spatial_size),
        )

    # Add random edges
    nodes = list(range(num_entities))
    for _ in range(num_edges):
        if len(nodes) >= 2:
            u, v = random.sample(nodes, 2)
            state.adjacency.add_edge(u, v)

    # Add all entities as nodes (even if they have no edges)
    for i in range(num_entities):
        if i not in state.adjacency:
            state.adjacency.add_node(i)

    return state


def create_circle_initial_state(num_points: int = 1000, radius: float = 10.0) -> SubstrateState:
    """
    Create entities positioned exactly on a perfect circle in the XY plane.

    This is ideal for validating π measurement - should yield π ≈ 3.14159.

    Args:
        num_points: Number of entities on the circle (more = better approximation)
        radius: Radius of the circle

    Returns:
        Initial substrate state with entities on perfect circle
    """
    import networkx as nx
    import math

    state = SubstrateState()

    # Place entities on a perfect circle in XY plane (Z=0)
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        state.entities[i] = {}
        state.positions[i] = (
            radius * math.cos(angle),
            radius * math.sin(angle),
            0.0,  # All on Z=0 plane
        )
        state.adjacency.add_node(i)

    # Connect adjacent points on the circle
    for i in range(num_points):
        next_i = (i + 1) % num_points
        state.adjacency.add_edge(i, next_i)

    return state


def create_ring_initial_state(num_entities: int = 10, radius: float = 10.0) -> SubstrateState:
    """
    Create an initial state with entities arranged in a ring in 3D space.

    Args:
        num_entities: Number of entities in the ring
        radius: Radius of the ring

    Returns:
        Initial substrate state with spatial embedding
    """
    import networkx as nx
    import math

    state = SubstrateState()

    # Create entities positioned in a circle on the XY plane
    for i in range(num_entities):
        state.entities[i] = {}
        angle = 2 * math.pi * i / num_entities
        state.positions[i] = (
            radius * math.cos(angle),
            radius * math.sin(angle),
            0.0,  # All on the same Z plane
        )

    # Create ring topology
    for i in range(num_entities):
        next_i = (i + 1) % num_entities
        state.adjacency.add_edge(i, next_i)

    return state


def create_star_initial_state(num_satellites: int = 9, radius: float = 10.0) -> SubstrateState:
    """
    Create an initial state with a star topology (one central node) in 3D space.

    Args:
        num_satellites: Number of satellite entities
        radius: Distance of satellites from center

    Returns:
        Initial substrate state with spatial embedding
    """
    import networkx as nx
    import random
    import math

    state = SubstrateState()

    # Entity 0 is the center at origin
    num_entities = num_satellites + 1
    state.entities[0] = {}
    state.positions[0] = (0.0, 0.0, 0.0)

    # Satellites distributed around center in 3D
    for i in range(1, num_entities):
        state.entities[i] = {}
        # Random point on sphere of given radius
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        state.positions[i] = (
            radius * math.sin(phi) * math.cos(theta),
            radius * math.sin(phi) * math.sin(theta),
            radius * math.cos(phi),
        )

    # Connect all satellites to center
    for i in range(1, num_entities):
        state.adjacency.add_edge(0, i)

    return state


def create_grid_initial_state(grid_size: int = 10, spacing: float = 2.0) -> SubstrateState:
    """
    Create an initial state with entities arranged in a 3D grid.

    This provides uniform spatial distribution ideal for measuring geometric π.

    Args:
        grid_size: Number of entities per dimension (total = grid_size^3)
        spacing: Distance between grid points

    Returns:
        Initial substrate state with grid embedding
    """
    import networkx as nx
    import math

    state = SubstrateState()

    entity_id = 0
    # Create 3D grid of entities
    for i in range(grid_size):
        for j in range(grid_size):
            for k in range(grid_size):
                state.entities[entity_id] = {}
                state.positions[entity_id] = (
                    i * spacing,
                    j * spacing,
                    k * spacing,
                )
                state.adjacency.add_node(entity_id)
                entity_id += 1

    # Connect nearest neighbors (within spacing * 1.5)
    entities = list(state.entities.keys())
    connection_threshold = spacing * 1.5

    for i, eid1 in enumerate(entities):
        for eid2 in entities[i+1:]:
            pos1 = state.positions[eid1]
            pos2 = state.positions[eid2]

            dist = math.sqrt(
                (pos1[0] - pos2[0])**2 +
                (pos1[1] - pos2[1])**2 +
                (pos1[2] - pos2[2])**2
            )

            if dist <= connection_threshold:
                state.adjacency.add_edge(eid1, eid2)

    return state
