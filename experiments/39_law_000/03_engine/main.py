import os
import math
import time
from history_visualization import HistoryVisualization
from law000 import apply_law000
from png_generator import heatmap_to_png, gen_animation
from substrate import Substrate
from snapshot_3d_exporter import SnapshotExporter3D
from tick_engine import TickEngine
from visualization_engine import VisualizationEngine

ROOT = 0
HORIZON = 100
SAMPLE_INTERVAL = 25
MAX_VISUALIZATIONS = 40  # Stop after this many visualizations
BUFFER_SIZE = 200  # Keep last 200 tick snapshots


def compute_parity(graph, state):
    """Compute parity based on quaternion magnitude of neighbors"""
    parity_map = {}
    for node, neighbors in graph.items():
        # Sum the magnitudes of imaginary parts (x, y, z) of neighbor quaternions
        imaginary_sum = 0.0
        for n in neighbors:
            q = state[n]
            # Magnitude of imaginary part: sqrt(x^2 + y^2 + z^2)
            imaginary_sum += math.sqrt(q[1]**2 + q[2]**2 + q[3]**2)

        # Binary parity: 1 if imaginary_sum > 0.5, else 0
        parity_map[node] = 1 if imaginary_sum > 0.5 else 0
    return parity_map


def main():
    # Create output directories if they don't exist
    os.makedirs("frames", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Initial graph and quaternion states
    graph = {
        0: [1],
        1: [0, 2],
        2: [1]
    }
    # Quaternion initial states (w, x, y, z)
    initial_state = {
        0: (1.0, 0.0, 0.0, 0.0),  # identity quaternion
        1: (0.0, 1.0, 0.0, 0.0),  # i axis
        2: (0.0, 0.0, 1.0, 0.0)   # j axis
    }

    substrate = Substrate(graph, initial_state)

    # Create tick engine (runs simulation in background)
    tick_engine = TickEngine(
        substrate=substrate,
        compute_parity_fn=compute_parity,
        apply_law_fn=apply_law000,
        buffer_size=BUFFER_SIZE
    )

    # Create visualization engine (consumes ticks at its own pace)
    viz_engine = VisualizationEngine(
        tick_engine=tick_engine,
        sample_interval=SAMPLE_INTERVAL
    )

    # Visualization tools
    viz = HistoryVisualization(horizon=HORIZON)
    exporter = SnapshotExporter3D(horizon=HORIZON)

    print("Starting tick engine (background simulation)...")
    tick_engine.start()

    print(f"Visualization consuming every {SAMPLE_INTERVAL} ticks")
    print("=" * 80)

    visualization_count = 0

    try:
        while visualization_count < MAX_VISUALIZATIONS:
            # Non-blocking: check if visualization is ready
            result = viz_engine.get_next_visualization()

            if result is None:
                # Not ready yet, sleep briefly
                time.sleep(0.01)
                continue

            snapshot, delta_tick, edge_diff = result
            viz_start = time.time()

            # Process visualization
            t = snapshot.tick
            visualization_count += 1

            # Print statistics
            stats = viz_engine.get_stats()
            print(f"\n[Viz {visualization_count}] Tick {t} (dt={delta_tick}, lag={stats['tick_lag']} ticks)")
            print(f"  Graph: {len(snapshot.graph)} nodes")
            print(f"  Edges: +{len(edge_diff['added_edges'])} -{len(edge_diff['removed_edges'])}")
            print(f"  Buffer: {stats['buffer_size']} snapshots {stats['buffer_range']}")

            # Show some quaternion values
            nodes = list(snapshot.state.keys())[:3]
            for n in nodes:
                q = snapshot.state[n]
                print(f"  Node {n}: q=({q[0]:.3f}, {q[1]:.3f}, {q[2]:.3f}, {q[3]:.3f})")

            # Render and export
            ascii_map = viz.render(edge_diff)
            heatmap_to_png(ascii_map, f"frames/frame_{t:06d}.png")

            edges = edge_diff['added_edges'] + edge_diff['removed_edges']
            points = exporter.snapshot_to_points(edges, t, snapshot.state)
            exporter.export_json(points, f"output/snapshot_{t:06d}.json")
            exporter.export_csv(points, f"output/snapshot_{t:06d}.csv")

            # NOTE: Do NOT modify substrate here - tick engine maintains its own state!
            # substrate.collapse_to_last_n_edges(1)  # REMOVED

            # Mark visualization complete
            viz_time = time.time() - viz_start
            viz_engine.mark_processing_complete(viz_time)

    finally:
        print("\n" + "=" * 80)
        print("Stopping tick engine...")
        tick_engine.stop()

        final_stats = viz_engine.get_stats()
        print(f"Final stats:")
        print(f"  Visualizations: {visualization_count}")
        print(f"  Last visualized tick: {final_stats['last_visualized_tick']}")
        print(f"  Latest tick: {final_stats['latest_tick']}")
        print(f"  Total tick lag: {final_stats['tick_lag']}")

        if visualization_count > 1:
            print("\nGenerating animation...")
            gen_animation()
            print("Done!")
        else:
            print("\nSkipping animation (need at least 2 frames)")


if __name__ == "__main__":
    main()
