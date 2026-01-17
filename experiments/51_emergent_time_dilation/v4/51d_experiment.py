#!/usr/bin/env python3
"""
Experiment 51d: Emergent Gravitational Field via Local Saturation Diffusion

Space is a 2D grid of sample-entities (cells).
A planet is a cluster of higher-cost cells around the center.
Each cell has local capacity, and saturation (load) diffuses between neighbors.
We test whether this produces a smooth time-dilation gradient gamma(r).
"""

import math
import random
from dataclasses import dataclass
from typing import Dict, Tuple, List

import numpy as np
import matplotlib.pyplot as plt


# =========================
# Sample cell (space atom)
# =========================

@dataclass
class SampleCell:
    i: int
    j: int
    tick_budget: int

    busy: bool = False
    remaining_work: int = 0

    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0

    def start_tick(self) -> None:
        if self.busy:
            return
        self.busy = True
        self.remaining_work = self.tick_budget
        self.ticks_processed += 1

    def work_one_unit(self) -> None:
        if not self.busy:
            return
        if self.remaining_work > 0:
            self.remaining_work -= 1
            if self.remaining_work == 0:
                self.busy = False

    def advance_substrate_tick(self) -> None:
        self.substrate_ticks_elapsed += 1

    @property
    def gamma_eff(self) -> float:
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed


# =========================
# Simulation 51d
# =========================

class Simulation51d:
    """
    Experiment 51d: space as a grid of sample-entities with local saturation diffusion.
    """

    def __init__(
            self,
            grid_size: int = 100,
            planet_radius: float = 10.0,
            planet_tick_budget: int = 5,
            space_tick_budget: int = 1,
            base_capacity: float = 1.0,
            diffusion_alpha: float = 0.2,
            capacity_sensitivity: float = 0.5,
            num_substrate_ticks: int = 20000,
    ):
        self.grid_size = grid_size
        self.planet_radius = planet_radius
        self.planet_tick_budget = planet_tick_budget
        self.space_tick_budget = space_tick_budget
        self.base_capacity = base_capacity
        self.diffusion_alpha = diffusion_alpha
        self.capacity_sensitivity = capacity_sensitivity
        self.num_substrate_ticks = num_substrate_ticks

        self.center = (grid_size // 2, grid_size // 2)

        self.cells: Dict[Tuple[int, int], SampleCell] = {}
        self.load_field = np.zeros((grid_size, grid_size), dtype=float)

    def setup(self) -> None:
        print("Setting up grid for Experiment 51d...")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cx, cy = self.center
                dx = i - cx
                dy = j - cy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= self.planet_radius:
                    tick_budget = self.planet_tick_budget
                else:
                    tick_budget = self.space_tick_budget
                self.cells[(i, j)] = SampleCell(i=i, j=j, tick_budget=tick_budget)

        print(f"Grid size: {self.grid_size}x{self.grid_size}")
        print(f"Planet radius: {self.planet_radius}")
        print(f"Planet tick_budget: {self.planet_tick_budget}")
        print(f"Space tick_budget: {self.space_tick_budget}")
        print(f"Base capacity per cell: {self.base_capacity}")
        print(f"Diffusion alpha: {self.diffusion_alpha}")
        print(f"Capacity sensitivity: {self.capacity_sensitivity}")
        print()

    def _compute_raw_load(self) -> np.ndarray:
        """
        Compute raw load L(x) based on local demand vs base capacity.
        Simple heuristic: demand = tick_budget if busy or about to start.
        """
        L = np.zeros_like(self.load_field)
        for (i, j), cell in self.cells.items():
            demand = cell.tick_budget
            L[i, j] = demand / max(self.base_capacity, 1e-6)
        return L

    def _diffuse_load(self, L: np.ndarray) -> np.ndarray:
        """
        Diffuse load using a discrete Laplacian with 4-neighbor stencil.
        L'(x) = L(x) + alpha * sum_{n in N(x)} (L(n) - L(x))
        """
        padded = np.pad(L, 1, mode="edge")
        center = padded[1:-1, 1:-1]
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]

        laplacian = (up + down + left + right - 4 * center)
        L_new = L + self.diffusion_alpha * laplacian
        L_new = np.clip(L_new, 0.0, None)
        return L_new

    def _effective_capacity(self, L: np.ndarray) -> np.ndarray:
        """
        Compute effective capacity per cell from load field.
        C_eff(x) = base_capacity / (1 + sensitivity * L(x))
        """
        return self.base_capacity / (1.0 + self.capacity_sensitivity * L)

    def run(self) -> None:
        print(f"Running Experiment 51d for {self.num_substrate_ticks} substrate ticks...\n")

        # initialize load field as zeros
        self.load_field[:, :] = 0.0

        for tick in range(self.num_substrate_ticks):
            # 1) advance substrate time
            for cell in self.cells.values():
                cell.advance_substrate_tick()

            # 2) compute raw load and diffuse it
            raw_load = self._compute_raw_load()
            self.load_field = self._diffuse_load(raw_load)

            # 3) compute effective capacity per cell
            C_eff = self._effective_capacity(self.load_field)

            # 4) apply capacity to BUSY and IDLE cells
            #    we treat capacity as "work units" available per cell this tick
            #    if capacity >= 1, we can do one unit of work
            #    if capacity >= tick_budget and cell is idle, we can start a new tick
            for (i, j), cell in self.cells.items():
                cap = C_eff[i, j]

                # process busy cell
                if cell.busy and cap >= 1.0:
                    cell.work_one_unit()
                    cap -= 1.0

                # possibly start new tick if idle and enough capacity
                if (not cell.busy) and cap >= cell.tick_budget:
                    cell.start_tick()
                    # we conceptually consume tick_budget units, but we don't
                    # track remaining capacity further here (single-step heuristic)

            if (tick + 1) % (self.num_substrate_ticks // 10) == 0:
                print(f"  Tick {tick + 1}/{self.num_substrate_ticks}")

        print("\nSimulation complete.\n")

    def measure_radial_gamma(self) -> List[Tuple[float, float, SampleCell]]:
        cx, cy = self.center
        max_r = min(cx, self.grid_size - cx - 1)
        radii = [r for r in range(1, max_r, 5)]

        results: List[Tuple[float, float, SampleCell]] = []

        print("=" * 70)
        print("EXPERIMENT 51d: RADIAL TIME DILATION RESULTS")
        print("=" * 70)
        print()
        print(f"{'r':<8} {'gamma_eff':<10} {'ticks_proc':<12} {'ticks_substrate':<16} {'tick_budget':<12}")
        print("-" * 70)

        for r in radii:
            i = cx + r
            j = cy
            cell = self.cells[(i, j)]
            gamma = cell.gamma_eff
            print(f"{r:<8} {gamma:<10.3f} {cell.ticks_processed:<12} {cell.substrate_ticks_elapsed:<16} {cell.tick_budget:<12}")
            results.append((float(r), gamma, cell))

        print()
        return results

    def analyze_gradient(self, results: List[Tuple[float, float, SampleCell]]) -> None:
        print("=" * 70)
        print("GRADIENT ANALYSIS")
        print("=" * 70)
        print()

        if not results:
            print("No radial samples found.")
            return

        results_sorted = sorted(results, key=lambda x: x[0])
        distances = np.array([r[0] for r in results_sorted], dtype=float)
        gammas = np.array([r[1] for r in results_sorted], dtype=float)

        increases = sum(1 for i in range(len(gammas) - 1) if gammas[i + 1] > gammas[i])
        total_pairs = len(gammas) - 1

        print(f"Monotonic increases: {increases}/{total_pairs}")
        if increases >= total_pairs * 0.7:
            print("[TENTATIVE SUCCESS] gamma_eff tends to increase with distance")
        else:
            print("[WARN] No clear monotonic gradient in gamma_eff(r)")
        print()

        print("Falloff Pattern Analysis:")
        dilation_depth = 1.0 - gammas
        inv_r2 = 1.0 / (distances ** 2)

        k_values = dilation_depth * (distances ** 2)
        k_mean = float(np.mean(k_values))
        k_std = float(np.std(k_values))

        print(f"  Fitting: (1 - gamma) ≈ k / r²")
        print(f"  Best fit k: {k_mean:.4f} ± {k_std:.4f}")

        predicted = k_mean / (distances ** 2)
        residuals = dilation_depth - predicted
        rmse = float(np.sqrt(np.mean(residuals ** 2)))

        print(f"  RMSE: {rmse:.4f}")
        if rmse < 0.05:
            print("  [TENTATIVE SUCCESS] Reasonable fit to 1/r² falloff")
        else:
            print("  [WARN] Poor fit to 1/r² pattern")
        print()

    def visualize(self, results: List[Tuple[float, float, SampleCell]]) -> None:
        if not results:
            print("No results to visualize.")
            return

        distances = np.array([r[0] for r in results], dtype=float)
        gammas = np.array([r[1] for r in results], dtype=float)

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(distances, gammas, 'bo-', linewidth=2, markersize=6)
        plt.axhline(y=1.0, color='r', linestyle='--', label='gamma=1.0 (no dilation)')
        plt.xlabel('Distance r from center', fontsize=12)
        plt.ylabel('gamma_eff', fontsize=12)
        plt.title('Emergent Time Dilation vs Distance (Experiment 51d)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim([0, 1.05])

        plt.subplot(1, 2, 2)
        dilation_depth = 1.0 - gammas
        inv_r2 = 1.0 / (distances ** 2)

        plt.plot(inv_r2, dilation_depth, 'rs-', linewidth=2, markersize=6)
        plt.xlabel('1 / r²', fontsize=12)
        plt.ylabel('1 - gamma_eff', fontsize=12)
        plt.title('Dilation Depth vs 1/r²', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('time_dilation_results_51d.png', dpi=150, bbox_inches='tight')
        print("Visualization saved to: time_dilation_results_51d.png\n")
        plt.show()


# =========================
# Main
# =========================

def main():
    print()
    print("=" * 70)
    print(" EXPERIMENT 51d: EMERGENT GRAVITATIONAL FIELD VIA LOCAL DIFFUSION")
    print("=" * 70)
    print()
    print("Space is a 2D grid of sample-entities.")
    print("A planet is a cluster of higher-cost cells around the center.")
    print("Local saturation diffuses between neighboring cells.")
    print()

    sim = Simulation51d(
        grid_size=100,
        planet_radius=10.0,
        planet_tick_budget=5,
        space_tick_budget=1,
        base_capacity=1.0,
        diffusion_alpha=0.2,
        capacity_sensitivity=0.5,
        num_substrate_ticks=20000,
    )

    sim.setup()
    sim.run()
    results = sim.measure_radial_gamma()
    sim.analyze_gradient(results)
    sim.visualize(results)

    print("=" * 70)
    print("VERDICT (51d, exploratory)")
    print("=" * 70)
    print()
    print("Look at:")
    print("  - smoothness and monotonicity of gamma_eff(r)")
    print("  - whether (1 - gamma) vs 1/r² shows a coherent pattern")
    print()
    print("This is NOT a proof of gravity, just a probe:")
    print("  - Does local diffusion of saturation between sample-entities")
    print("    produce an emergent gravitational-like time-dilation field?")
    print()


if __name__ == "__main__":
    main()
