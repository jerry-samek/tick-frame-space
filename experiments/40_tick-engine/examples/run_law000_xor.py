"""
Example: Running Law-000 XOR

Demonstrates the theoretical baseline law with binary states and XOR evolution.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time

from tick_engine.core import Substrate, TickEngine, VisualizationEngine
from tick_engine.laws import Law000_XOR, create_line_graph


def main():
    print("=" * 80)
    print("LAW-000 XOR: Theoretical Baseline Evolution")
    print("=" * 80)

    # Create law instance
    law = Law000_XOR()

    # Create initial graph (5-node line with middle activated)
    graph, initial_state = create_line_graph(5)

    print(f"\nInitial graph: {graph}")
    print(f"Initial state: {initial_state}")
    print(f"Law: {law.name}")
    print(f"Description: {law.description}\n")

    # Create substrate with law
    substrate = Substrate(graph, initial_state, law)

    # Create tick engine
    engine = TickEngine(
        substrate=substrate,
        buffer_size=100,
        collapse_interval=5,  # Collapse frequently to prevent explosion
        collapse_size=10       # Keep 10 edges
    )

    # Create visualization engine
    viz = VisualizationEngine(
        tick_engine=engine,
        law=law,
        sample_interval=5  # Visualize every 5 ticks
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
        print(f"  Graph: {len(snapshot.graph)} nodes, {len(edge_diff['added_edges'])} new edges")

        # Show node states (first 10 only)
        print("  States:", end=" ")
        for node_id in sorted(snapshot.state.keys())[:10]:
            state = snapshot.state[node_id]
            symbol = "X" if state == 1 else "."
            print(f"{node_id}:{symbol}", end=" ")
        if len(snapshot.state) > 10:
            print("...", end="")
        print()

        # Show 3D visualization data
        points = viz.render_3d_points(snapshot)
        print(f"  3D points: {len(points)} rendered")

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
    print("\nLaw-000 XOR demonstration complete!")


if __name__ == "__main__":
    main()
