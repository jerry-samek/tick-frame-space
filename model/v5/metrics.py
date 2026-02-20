"""Metrics tracking for v5 simulation -- CSV output for analysis."""

import csv
import os


class MetricsTracker:
    """Writes per-tick summary and per-entity data to CSV files."""

    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)

        self._summary_path = os.path.join(output_dir, "summary.csv")
        self._entity_path = os.path.join(output_dir, "entities.csv")

        self._summary_file = open(self._summary_path, "w", newline="")
        self._entity_file = open(self._entity_path, "w", newline="")

        self._summary_writer = csv.writer(self._summary_file)
        self._entity_writer = csv.writer(self._entity_file)

        self._summary_writer.writerow([
            "tick", "entity_count", "total_system_energy",
            "total_entity_energy", "total_field_energy",
            "field_min", "field_max", "field_mean",
            "photon_max", "photon_mean",
            "replication_events", "dissolution_events",
            "max_generation",
            "blocked_moves", "trapped_entities", "failed_replications",
        ])
        self._entity_writer.writerow([
            "tick", "entity_id", "q", "r",
            "memory_size", "memory_fill_pct",
            "heading_x", "heading_y",
            "hill_height", "generation",
        ])

    def log(self, world) -> None:
        tick = world.tick

        self._summary_writer.writerow([
            tick,
            world.entity_count(),
            f"{world.total_system_energy():.4f}",
            f"{world.total_entity_energy():.4f}",
            f"{world.field.total_energy():.4f}",
            f"{world.field.min_value():.4f}",
            f"{world.field.max_value():.4f}",
            f"{world.field.mean_value():.4f}",
            f"{world.photon_field.max_value():.4f}",
            f"{world.photon_field.mean_value():.4f}",
            world.replication_events,
            world.dissolution_events,
            world.max_generation,
            world.blocked_moves,
            world.trapped_entities,
            world.failed_replications,
        ])

        for e in world.entities:
            q, r = e.pos
            hx, hy = e.heading()
            hill = world.field.value_at(e.pos)
            self._entity_writer.writerow([
                tick, e.id, q, r,
                e.memory_size, f"{e.memory_fill_pct:.4f}",
                f"{hx:.4f}", f"{hy:.4f}",
                f"{hill:.4f}", e.generation,
            ])

        if tick % 100 == 0:
            self._summary_file.flush()
            self._entity_file.flush()

    def close(self) -> None:
        self._summary_file.close()
        self._entity_file.close()
