import json
import csv


class SnapshotExporter3D:
    def __init__(self, horizon=10):
        self.horizon = horizon

    # ----------------------------------------
    # Convert collapse window to 3D point cloud
    # ----------------------------------------
    def snapshot_to_points(self, edges, tick):
        """
        edges: list of (a, b) tuples already sorted by time
        tick: current global tick
        """
        points = []
        node_ids = [a for a, b in edges] + [b for a, b in edges]
        min_id = min(node_ids)
        max_id = max(node_ids)

        width = max_id - min_id + 1
        height = len(edges)  # nebo horizon
        for idx, (a, b) in enumerate(edges):
            # 3D coordinates
            x = hash(a) % width
            y = hash(idx) % height
            z = tick  # global time

            points.append({
                "tick": tick,
                "edge_index": idx,
                "node_a": a,
                "node_b": b,
                "x": x,
                "y": y,
                "z": z
            })

        return points

    # ----------------------------------------
    # Export to JSON
    # ----------------------------------------
    def export_json(self, points, filename):
        with open(filename, "w") as f:
            json.dump(points, f, indent=2)

    # ----------------------------------------
    # Export to CSV
    # ----------------------------------------
    def export_csv(self, points, filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "edge_index", "node_a", "node_b", "x", "y", "z"])
            for p in points:
                writer.writerow([
                    p["tick"], p["edge_index"], p["node_a"], p["node_b"],
                    p["x"], p["y"], p["z"]
                ])
