import csv
import os

import numpy as np


# ==========================
# CSV Output (hex grid)
# ==========================

class CSVLogger:
    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.entity_file = open(os.path.join(output_dir, "entities_hex.csv"), "w", newline="")
        self.summary_file = open(os.path.join(output_dir, "summary_hex.csv"), "w", newline="")
        self.entity_writer = csv.writer(self.entity_file)
        self.summary_writer = csv.writer(self.summary_file)

        self.entity_writer.writerow([
            "tick", "entity_id", "q", "r", "baseline_h", "current_h", "energy",
            "delta_h", "delta_delta_h", "memory", "window_size", "pattern", "age"
        ])
        self.summary_writer.writerow([
            "tick", "entity_count", "total_energy", "avg_delta_h", "min_delta_h",
            "max_delta_h", "max_hill_height", "total_imprint", "total_leak",
            "replication_events", "merge_events"
        ])

    def log_tick(self, tick: int, world):
        entities = world.entities

        for e in entities:
            current_h = world.hill.height_at(e.q, e.r)
            mem_str = "".join(str(int(m)) for m in e.memory)
            self.entity_writer.writerow([
                tick, e.id, e.q, e.r, f"{e.baseline_h:.4f}", f"{current_h:.4f}",
                f"{e.energy:.4f}", f"{e.delta_h:.4f}", f"{e.delta_delta_h:.4f}",
                mem_str, len(e.memory), f"{e.pattern:.4f}", e.age
            ])

        if entities:
            delta_hs = [e.delta_h for e in entities]
            total_energy = sum(e.energy for e in entities)
            avg_dh = np.mean(delta_hs)
            min_dh = min(delta_hs)
            max_dh = max(delta_hs)
        else:
            total_energy = 0.0
            avg_dh = min_dh = max_dh = 0.0

        self.summary_writer.writerow([
            tick, len(entities), f"{total_energy:.4f}",
            f"{avg_dh:.4f}", f"{min_dh:.4f}", f"{max_dh:.4f}",
            f"{np.max(world.hill.height):.4f}",
            f"{np.sum(world.imprint_field):.4f}",
            f"{np.sum(world.leak_field):.4f}",
            world.replication_events, world.merge_events
        ])

        if tick % 100 == 0:
            self.entity_file.flush()
            self.summary_file.flush()

    def close(self):
        self.entity_file.close()
        self.summary_file.close()
