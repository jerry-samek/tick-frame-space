import json
import csv


class SnapshotExporter3D:
    def __init__(self, horizon=10):
        self.horizon = horizon

    # ----------------------------------------
    # Convert collapse window to 3D point cloud
    # ----------------------------------------
    def snapshot_to_points(self, edges, tick, state):
        """
        edges: list of (a, b) tuples already sorted by time
        tick: current global tick
        state: dict mapping node -> quaternion (w, x, y, z)
        """
        points = []

        for idx, (a, b) in enumerate(edges):
            # Get quaternions for both nodes
            q_a = state.get(a, (1.0, 0.0, 0.0, 0.0))
            q_b = state.get(b, (1.0, 0.0, 0.0, 0.0))

            # Average the quaternion positions for this edge
            # Use imaginary parts (i, j, k) as 3D coordinates
            x = (q_a[1] + q_b[1]) / 2.0  # i component
            y = (q_a[2] + q_b[2]) / 2.0  # j component
            z = (q_a[3] + q_b[3]) / 2.0  # k component

            points.append({
                "tick": tick,
                "edge_index": idx,
                "node_a": a,
                "node_b": b,
                "x": x,
                "y": y,
                "z": z,
                "q_a": q_a,
                "q_b": q_b
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
            writer.writerow(["tick", "edge_index", "node_a", "node_b", "x", "y", "z",
                           "qa_w", "qa_x", "qa_y", "qa_z", "qb_w", "qb_x", "qb_y", "qb_z"])
            for p in points:
                q_a = p.get("q_a", (0, 0, 0, 0))
                q_b = p.get("q_b", (0, 0, 0, 0))
                writer.writerow([
                    p["tick"], p["edge_index"], p["node_a"], p["node_b"],
                    p["x"], p["y"], p["z"],
                    q_a[0], q_a[1], q_a[2], q_a[3],
                    q_b[0], q_b[1], q_b[2], q_b[3]
                ])
