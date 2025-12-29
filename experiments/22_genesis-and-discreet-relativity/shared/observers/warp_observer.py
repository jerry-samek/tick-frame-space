# observers/warp_observer.py

from typing import Optional
import math

from .base import Observer


class WarpObserver(Observer):
    """
    Applies a warp-like coordinate transform to perceived positions.
    This implements the Tick‑Frame Alcubierre Metric as an observer-only effect.
    """

    def __init__(self, warp_center_id: int = 0, strength: float = 0.1, log_interval: int = 10, output_dir: Optional[str] = None):
        super().__init__(name="Warp", log_interval=log_interval, output_dir=output_dir)
        self.warp_center_id = warp_center_id
        self.strength = strength

    def warp_transform(self, x, c, s):
        dx = x - c
        if dx > 0:
            return c + dx * (1 - s)   # compress space in front
        else:
            return c + dx * (1 + s)   # stretch space behind

    def on_post_tick(self, state):
        tick = state.tick

        # Only run if positions exist
        if not hasattr(state, "positions"):
            return

        if self.warp_center_id not in state.positions:
            return

        cx, cy, cz = state.positions[self.warp_center_id]

        # Log warp metrics
        if self.should_log(tick):
            # Compute warp statistics
            total_displacement = 0.0
            max_displacement = 0.0
            num_entities = 0

            for eid, (x, y, z) in state.positions.items():
                # Warp each axis independently (simple 1D warp per axis)
                wx = self.warp_transform(x, cx, self.strength)
                wy = self.warp_transform(y, cy, self.strength)
                wz = self.warp_transform(z, cz, self.strength)

                # Calculate displacement
                displacement = math.sqrt((wx - x)**2 + (wy - y)**2 + (wz - z)**2)
                total_displacement += displacement
                max_displacement = max(max_displacement, displacement)
                num_entities += 1

                # Log individual entity warp data
                entity_data = {
                    "tick": tick,
                    "entity_id": eid,
                    "orig_x": x,
                    "orig_y": y,
                    "orig_z": z,
                    "warp_x": wx,
                    "warp_y": wy,
                    "warp_z": wz,
                    "displacement": displacement
                }
                self.log_csv("warp_positions.csv", entity_data)

            # Summary metrics
            avg_displacement = total_displacement / max(1, num_entities)
            summary_data = {
                "tick": tick,
                "warp_center_id": self.warp_center_id,
                "strength": self.strength,
                "avg_displacement": avg_displacement,
                "max_displacement": max_displacement,
                "num_entities": num_entities
            }
            self.log_csv("warp_metrics.csv", summary_data)

            # Summary text log
            summary = (
                f"[Warp t={tick}] "
                f"Center={self.warp_center_id}, Strength={self.strength:.3f}, "
                f"AvgDisp={avg_displacement:.3f}, MaxDisp={max_displacement:.3f}\n"
            )
            self.log_text("warp_log.txt", summary)
