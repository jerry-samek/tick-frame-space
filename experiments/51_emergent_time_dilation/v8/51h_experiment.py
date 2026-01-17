#!/usr/bin/env python3
"""
Experiment 51h: Smooth Gravitational Gradient

- Softened, long-range reaction–diffusion load field L(x)
- Extended per-cell energy dynamics with higher capacity and stronger load coupling
- Optional energy diffusion to smooth γ(r)
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

    # Load field parameters (softened, long-range)
    diffusion_alpha: float = 0.015  # higher than 51g
    damping_gamma: float = 0.0001  # lower than 51g
    source_scale: float = 0.5  # softer planet source

    # Energy dynamics (extended)
    energy_regen_rate: float = 1.0
    energy_max: float = 30.0  # higher capacity
    energy_load_drain: float = 0.03  # stronger coupling to load

    # Optional energy diffusion
    energy_diffusion_beta: float = 0.005  # 0.0 to disable

    # Simulation
    num_substrate_ticks: int = 20000

    name: str = "51h_baseline"


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

    def work_one_unit(self):
        if not self.busy:
            return
        if not self.can_start_or_continue():
            return
        self.remaining_work -= 1.0
        # consume energy proportional to tick_budget
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

class Simulation51h:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.center = (cfg.grid_size // 2, cfg.grid_size // 2)

        self.cells: Dict[Tuple[int, int], SampleCell] = {}
        self.load_field = np.zeros((cfg.grid_size, cfg.grid_size), dtype=float)
        self.energy_field = np.zeros((cfg.grid_size, cfg.grid_size), dtype=float)

    # --------------------------------------------------------

    def setup(self):
        print(f"Setting up Experiment 51h [{self.cfg.name}]...")

        for i in range(self.cfg.grid_size):
            for j in range(self.cfg.grid_size):
                cx, cy = self.center
                dist = math.dist((i, j), (cx, cy))

                if dist <= self.cfg.planet_radius:
                    tb = self.cfg.planet_tick_budget
                else:
                    tb = self.cfg.space_tick_budget

                energy_init = self.cfg.energy_max * 0.5

                cell = SampleCell(
                    i=i,
                    j=j,
                    tick_budget=tb,
                    energy=energy_init,
                )
                self.cells[(i, j)] = cell
                self.energy_field[i, j] = energy_init

        print("Setup complete.\n")

    # --------------------------------------------------------
    # LOAD FIELD DYNAMICS
    # --------------------------------------------------------

    def compute_source(self):
        S = np.zeros_like(self.load_field)
        for (i, j), cell in self.cells.items():
            S[i, j] = self.cfg.source_scale * cell.tick_budget
        return S

    def diffuse(self, field, alpha):
        padded = np.pad(field, 1, mode="edge")
        center = padded[1:-1, 1:-1]
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]

        lap = (up + down + left + right - 4 * center)
        return field + alpha * lap

    def update_load_field(self):
        L = self.load_field
        S = self.compute_source()

        # diffusion
        L = self.diffuse(L, self.cfg.diffusion_alpha)

        # source
        L = L + S

        # nonlinear damping
        L = L - self.cfg.damping_gamma * (L ** 2)

        # clamp
        L = np.clip(L, 0.0, None)
        self.load_field = L

    # --------------------------------------------------------
    # ENERGY DYNAMICS
    # --------------------------------------------------------

    def update_energy_field(self):
        E = self.energy_field
        L = self.load_field

        # base regeneration
        E = E + self.cfg.energy_regen_rate

        # load-induced drain
        E = E - self.cfg.energy_load_drain * L

        # optional energy diffusion
        if self.cfg.energy_diffusion_beta > 0.0:
            E = self.diffuse(E, self.cfg.energy_diffusion_beta)

        # clamp
        E = np.clip(E, 0.0, self.cfg.energy_max)
        self.energy_field = E

        # sync back into cells
        for (i, j), cell in self.cells.items():
            cell.energy = self.energy_field[i, j]

    # --------------------------------------------------------

    def run(self):
        print(f"Running simulation [{self.cfg.name}] for {self.cfg.num_substrate_ticks} ticks...\n")

        for tick in range(self.cfg.num_substrate_ticks):
            # 1) advance substrate time
            for cell in self.cells.values():
                cell.advance_substrate_tick()

            # 2) update load field
            self.update_load_field()

            # 3) update energy field
            self.update_energy_field()

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
        sim = Simulation51h(cfg)
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
    cfg = Config(name="51h_baseline")
    sim = Simulation51h(cfg)
    sim.setup()
    sim.run()
    sim.measure_radial_gamma()

    # Example batch:
    configs = [
        Config(diffusion_alpha=0.01, damping_gamma=0.0001,
               energy_load_drain=0.02, name="soft_field_1"),
        Config(diffusion_alpha=0.02, damping_gamma=0.00005,
               energy_load_drain=0.04, name="soft_field_2"),
        Config(diffusion_alpha=0.015, damping_gamma=0.00015,
               energy_load_drain=0.03, energy_diffusion_beta=0.01,
               name="with_energy_diffusion"),
    ]
    results = run_batch(configs)
    print(results)
