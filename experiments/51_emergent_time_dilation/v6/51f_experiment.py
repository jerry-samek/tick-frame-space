#!/usr/bin/env python3
"""
Experiment 51f: Reaction–Diffusion Saturation Field with Nonlinear Damping
--------------------------------------------------------------------------

This version is designed for:
- easy parameter tuning,
- batch testing (parameter sweeps),
- clean modular structure,
- stable reaction–diffusion dynamics.

Everything is controlled through a Config object.
"""

import math
from dataclasses import dataclass
from typing import Dict, Tuple, List

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class Config:
    grid_size: int = 100

    planet_radius: float = 10.0
    planet_tick_budget: float = 1.5
    space_tick_budget: float = 1.0

    base_capacity: float = 1.0
    capacity_sensitivity: float = 0.03
    capacity_min: float = 0.25

    diffusion_alpha: float = 0.005
    damping_gamma: float = 0.0005  # nonlinear damping coefficient

    num_substrate_ticks: int = 20000

    name: str = "default"


# ============================================================
# SAMPLE CELL
# ============================================================

@dataclass
class SampleCell:
    i: int
    j: int
    tick_budget: float

    busy: bool = False
    remaining_work: float = 0.0

    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0

    def start_tick(self):
        if self.busy:
            return
        self.busy = True
        self.remaining_work = self.tick_budget
        self.ticks_processed += 1

    def work_one_unit(self):
        if not self.busy:
            return
        self.remaining_work -= 1.0
        if self.remaining_work <= 0:
            self.busy = False

    def advance_substrate_tick(self):
        self.substrate_ticks_elapsed += 1

    @property
    def gamma_eff(self):
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed


# ============================================================
# SIMULATION
# ============================================================

class Simulation51f:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.center = (cfg.grid_size // 2, cfg.grid_size // 2)

        self.cells: Dict[Tuple[int, int], SampleCell] = {}
        self.load_field = np.zeros((cfg.grid_size, cfg.grid_size), dtype=float)

    # --------------------------------------------------------

    def setup(self):
        print(f"Setting up Experiment 51f [{self.cfg.name}]...")

        for i in range(self.cfg.grid_size):
            for j in range(self.cfg.grid_size):
                cx, cy = self.center
                dist = math.dist((i, j), (cx, cy))

                if dist <= self.cfg.planet_radius:
                    tb = self.cfg.planet_tick_budget
                else:
                    tb = self.cfg.space_tick_budget

                self.cells[(i, j)] = SampleCell(i=i, j=j, tick_budget=tb)

        print("Setup complete.\n")

    # --------------------------------------------------------

    def compute_source(self):
        S = np.zeros_like(self.load_field)
        for (i, j), cell in self.cells.items():
            S[i, j] = cell.tick_budget
        return S

    # --------------------------------------------------------

    def diffuse(self, L):
        padded = np.pad(L, 1, mode="edge")
        center = padded[1:-1, 1:-1]
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]

        lap = (up + down + left + right - 4 * center)
        return L + self.cfg.diffusion_alpha * lap

    # --------------------------------------------------------

    def nonlinear_damping(self, L):
        return L - self.cfg.damping_gamma * (L ** 2)

    # --------------------------------------------------------

    def effective_capacity(self, L):
        C = self.cfg.base_capacity / (1 + self.cfg.capacity_sensitivity * L)
        return np.maximum(C, self.cfg.capacity_min)

    # --------------------------------------------------------

    def run(self):
        print(f"Running simulation [{self.cfg.name}] for {self.cfg.num_substrate_ticks} ticks...\n")

        for tick in range(self.cfg.num_substrate_ticks):
            for cell in self.cells.values():
                cell.advance_substrate_tick()

            S = self.compute_source()

            L = self.load_field
            L = self.diffuse(L)
            L = L + S
            L = self.nonlinear_damping(L)

            L = np.clip(L, 0.0, None)
            self.load_field = L

            C_eff = self.effective_capacity(L)

            for (i, j), cell in self.cells.items():
                cap = C_eff[i, j]

                if cell.busy and cap >= 1.0:
                    cell.work_one_unit()
                    cap -= 1.0

                if (not cell.busy) and cap >= cell.tick_budget:
                    cell.start_tick()

            if (tick + 1) % (self.cfg.num_substrate_ticks // 10) == 0:
                print(f"  Tick {tick + 1}/{self.cfg.num_substrate_ticks}")

        print("\nSimulation complete.\n")

    # --------------------------------------------------------

    def measure_radial_gamma(self):
        cx, cy = self.center
        max_r = min(cx, self.cfg.grid_size - cx - 1)
        radii = [r for r in range(1, max_r, 5)]

        results = []

        print("Radial γ_eff:")
        for r in radii:
            cell = self.cells[(cx + r, cy)]
            results.append((r, cell.gamma_eff))
            print(f"  r={r:3d}  γ={cell.gamma_eff:.4f}")

        print()
        return results


# ============================================================
# BATCH TESTING
# ============================================================

def run_batch(configs: List[Config]):
    all_results = {}
    for cfg in configs:
        sim = Simulation51f(cfg)
        sim.setup()
        sim.run()
        results = sim.measure_radial_gamma()
        all_results[cfg.name] = results
    return all_results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # cfg = Config(name="baseline_51f")
    # sim = Simulation51f(cfg)
    # sim.setup()
    # sim.run()
    # sim.measure_radial_gamma()

    # Example batch:
    configs = [
        Config(diffusion_alpha=0.003, damping_gamma=0.0003, name="low_alpha_low_gamma"),
        Config(diffusion_alpha=0.005, damping_gamma=0.0005, name="mid_alpha_mid_gamma"),
        Config(diffusion_alpha=0.01, damping_gamma=0.0010, name="high_alpha_high_gamma"),
    ]
    results = run_batch(configs)
    print(results)
