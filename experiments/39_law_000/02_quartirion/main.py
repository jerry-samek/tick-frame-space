import os
from history_visualization import HistoryVisualization
from law000 import apply_law000
from observer import Observer
from png_generator import heatmap_to_png, gen_animation
from substrate import Substrate
from tick_emitter import TickEmitter
from snapshot_3d_exporter import SnapshotExporter3D

ROOT = 0
HORIZON = 100
SAMPLE_INTERVAL = 25
MAX_TICKS=1000


def main():
    # Create output directories if they don't exist
    os.makedirs("frames", exist_ok=True)
    os.makedirs("output", exist_ok=True)

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
    observer = Observer(substrate, sample_interval=SAMPLE_INTERVAL)
    viz = HistoryVisualization(horizon=HORIZON)
    exporter = SnapshotExporter3D(horizon=HORIZON)
    ticks = TickEmitter()

    for _ in range(MAX_TICKS):
        t = ticks.next_tick()

        parity_map = compute_parity(substrate.graph, substrate.state)
        substrate.grow(parity_map)

        substrate.state = apply_law000(substrate.graph, substrate.state, t)

        # Horizon pruning
        # substrate.prune_to_horizon(ROOT, HORIZON)

        sample = observer.observe(t)

        if sample is not None:
            print(f"{t}")
            #  print_state(sample, t)
            ascii_map = viz.render(sample)
            heatmap_to_png(ascii_map, f"frames/frame_{t:06d}.png")

            # Extract edges from sample dict for 3D export
            edges = sample['added_edges'] + sample['removed_edges']
            points = exporter.snapshot_to_points(edges, t, substrate.state)

            exporter.export_json(points, f"output/snapshot_{t:06d}.json")
            exporter.export_csv(points, f"output/snapshot_{t:06d}.csv")

            # substrate.collapse_to_last_edge()
            substrate.collapse_to_last_n_edges(1)

    gen_animation()


def compute_parity(graph, state):
    """Compute parity based on quaternion magnitude of neighbors"""
    import math
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


if __name__ == "__main__":
    main()
