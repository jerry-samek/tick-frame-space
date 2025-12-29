"""
Example: Running Law-Quaternion

Demonstrates quaternion-based 3D evolution with spatial dynamics.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time

from tick_engine.core import Substrate, TickEngine, VisualizationEngine
from tick_engine.laws import LawQuaternion, create_3d_seed_graph


def main():
    print("=" * 80)
    print("LAW-QUATERNION: 3D Movement via Quaternion Algebra")
    print("=" * 80)

    # Create law instance
    law = LawQuaternion()

    # Create initial graph (3 nodes on different axes)
    graph, initial_state = create_3d_seed_graph()

    print(f"\nInitial graph: {graph}")
    print(f"Initial states:")
    for node_id, q in initial_state.items():
        print(f"  Node {node_id}: {law.state_summary(q)}")
    print(f"\nLaw: {law.name}")
    print(f"Description: {law.description}\n")

    # Create substrate with law
    substrate = Substrate(graph, initial_state, law)

    # Create tick engine
    engine = TickEngine(
        substrate=substrate,
        buffer_size=100,
        collapse_interval=10,  # Collapse every 10 ticks
        collapse_size=5         # Keep 5 edges
    )

    # Create visualization engine
    viz = VisualizationEngine(
        tick_engine=engine,
        law=law,
        sample_interval=10  # Visualize every 10 ticks
    )

    # Start simulation
    print("Starting tick engine...")
    engine.start()

    # Give it a moment to generate some ticks
    time.sleep(0.5)

    print(f"Engine running: {engine.running}")
    print(f"Buffer contains {engine.get_snapshot_count()} snapshots\n")

    # Consume and display visualizations
    print("Consuming visualizations:")
    print("-" * 80)

    viz_count = 0
    max_visualizations = 10

    while viz_count < max_visualizations:
        result = viz.get_next_visualization()

        if result is None:
            time.sleep(0.01)
            continue

        snapshot, delta_t, edge_diff = result
        viz_count += 1
        viz_start = time.time()

        # Display state
        print(f"\n[Viz {viz_count}] Tick {snapshot.tick} (dt={delta_t})")
        print(f"  Graph: {len(snapshot.graph)} nodes")
        print(f"  Edges: +{len(edge_diff['added_edges'])} -{len(edge_diff['removed_edges'])}")

        # Show quaternion states (sample first 3 nodes)
        sample_nodes = sorted(snapshot.state.keys())[:3]
        for node_id in sample_nodes:
            q = snapshot.state[node_id]
            coords = law.to_3d_coords(q)
            energy = law.state_energy(q)
            print(f"  Node {node_id}: {law.state_summary(q)}")
            print(f"    3D: ({coords[0]:.3f}, {coords[1]:.3f}, {coords[2]:.3f})")
            print(f"    Energy: {energy:.3f}")

        # Stats
        stats = viz.get_stats()
        print(f"  Lag: {stats['tick_lag']} ticks, Buffer: {stats['buffer_size']}")

        # Mark viz complete
        viz_time = time.time() - viz_start
        viz.mark_processing_complete(viz_time)

    # Stop engine
    print("\n" + "=" * 80)
    print("Stopping engine...")
    engine.stop()

    # Final stats
    final_stats = engine.get_stats()
    print(f"\nFinal Statistics:")
    print(f"  Total ticks: {final_stats['current_tick']}")
    print(f"  Visualizations: {viz_count}")
    print(f"  Law: {final_stats['law']}")
    print("\nLaw-Quaternion demonstration complete!")


if __name__ == "__main__":
    main()
