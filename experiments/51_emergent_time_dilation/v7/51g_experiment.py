#!/usr/bin/env python3
"""
Experiment 51g: Reaction–Diffusion Load + Regenerative Energy

- Dynamic load field L(x): reaction–diffusion with nonlinear damping
- Per-cell energy buffer E(x): regenerates every substrate tick, consumed by work
- Time dilation γ_eff emerges from how often cells manage to complete ticks
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

    # Load field parameters
    diffusion_alpha: float = 0.005
    damping_gamma: float = 0.0005  # nonlinear damping coefficient
    source_scale: float = 1.0  # scales tick_budget into load source

    # Energy dynamics
    energy_regen_rate: float = 1.0
    energy_max: float = 10.0
    energy_load_drain: float = 0.01  # how much load drains energy per tick

    # Simulation
    num_substrate_ticks: int = 20000

    name: str = "51g_default"


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

    energy: float = 0.0

    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0

    def advance_substrate_tick(self):
        self.substrate_ticks_elapsed += 1

    def can_start_or_continue(self):
        return self.energy >= self.tick_budget

    def start_tick(self):
        if self.busy:
            return
        if not self.can_start_or_continue():
            return
        self.busy = True
        self.remaining_work = self.tick_budget
        # energy is consumed gradually as work is done

    def work_one_unit(self):
        if not self.busy:
            return
        if not self.can_start_or_continue():
            return
        self.remaining_work -= 1.0
        self.energy -= self.tick_budget / max(self.tick_budget, 1.0)
        if self.remaining_work <= 0:
            self.busy = False
            self.ticks_processed += 1

    @property
    def gamma_eff(self):
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed


# ============================================================
# SIMULATION
# ============================================================

class Simulation51g:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.center = (cfg.grid_size // 2, cfg.grid_size // 2)

        self.cells: Dict[Tuple[int, int], SampleCell] = {}
        self.load_field = np.zeros((cfg.grid_size, cfg.grid_size), dtype=float)

    # --------------------------------------------------------

    def setup(self):
        print(f"Setting up Experiment 51g [{self.cfg.name}]...")

        for i in range(self.cfg.grid_size):
            for j in range(self.cfg.grid_size):
                cx, cy = self.center
                dist = math.dist((i, j), (cx, cy))

                if dist <= self.cfg.planet_radius:
                    tb = self.cfg.planet_tick_budget
                else:
                    tb = self.cfg.space_tick_budget

                self.cells[(i, j)] = SampleCell(
                    i=i,
                    j=j,
                    tick_budget=tb,
                    energy=self.cfg.energy_max / 2.0,  # start with half-full buffer
                )

        print("Setup complete.\n")

    # --------------------------------------------------------
    # LOAD FIELD DYNAMICS
    # --------------------------------------------------------

    def compute_source(self):
        S = np.zeros_like(self.load_field)
        for (i, j), cell in self.cells.items():
            S[i, j] = self.cfg.source_scale * cell.tick_budget
        return S

    def diffuse_load(self, L):
        padded = np.pad(L, 1, mode="edge")
        center = padded[1:-1, 1:-1]
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]

        lap = (up + down + left + right - 4 * center)
        return L + self.cfg.diffusion_alpha * lap

    def nonlinear_damping(self, L):
        return L - self.cfg.damping_gamma * (L ** 2)

    # --------------------------------------------------------
    # ENERGY DYNAMICS
    # --------------------------------------------------------

    def update_energy(self, L):
        for (i, j), cell in self.cells.items():
            # base regeneration
            cell.energy += self.cfg.energy_regen_rate

            # load-induced drain
            drain = self.cfg.energy_load_drain * L[i, j]
            cell.energy -= drain

            # clamp
            if cell.energy > self.cfg.energy_max:
                cell.energy = self.cfg.energy_max
            if cell.energy < 0.0:
                cell.energy = 0.0

    # --------------------------------------------------------

    def run(self):
        print(f"Running simulation [{self.cfg.name}] for {self.cfg.num_substrate_ticks} ticks...\n")

        for tick in range(self.cfg.num_substrate_ticks):
            # 1) advance substrate time
            for cell in self.cells.values():
                cell.advance_substrate_tick()

            # 2) update load field
            S = self.compute_source()
            L = self.load_field
            L = self.diffuse_load(L)
            L = L + S
            L = self.nonlinear_damping(L)
            L = np.clip(L, 0.0, None)
            self.load_field = L

            # 3) update energy buffers
            self.update_energy(L)

            # 4) perform work based on energy
            for (i, j), cell in self.cells.items():
                if cell.busy:
                    cell.work_one_unit()
                else:
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
        sim = Simulation51g(cfg)
        sim.setup()
        sim.run()
        results = sim.measure_radial_gamma()
        all_results[cfg.name] = results
    return all_results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Single baseline run
    cfg = Config(name="51g_baseline")
    sim = Simulation51g(cfg)
    sim.setup()
    sim.run()
    sim.measure_radial_gamma()

    # Example batch:
    configs = [
        Config(energy_load_drain=0.005, name="drain_0.005"),
        Config(energy_load_drain=0.01, name="drain_0.01"),
        Config(energy_load_drain=0.02, name="drain_0.02"),
    ]
    results = run_batch(configs)
    print(results)
