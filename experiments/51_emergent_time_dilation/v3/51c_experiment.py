#!/usr/bin/env python3
"""
Experiment 51c: Emergent Time Dilation in a Sample-Entity Space

Goal:
  - Represent space as a 2D grid of sample-entities (cells),
  - Represent a "planet" as a cluster of higher-cost cells,
  - Use local (chunk-based) capacity instead of a global scheduler,
  - Measure whether a smooth time-dilation gradient γ(r) emerges
    around the planetary region without any explicit distance-based formulas.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import numpy as np


# =========================
# Sample cell (space atom)
# =========================

@dataclass
class SampleCell:
    """
    A sample-entity representing a small region of space.

    - tick_budget: how much work is needed for one "physical" tick
    - busy: whether the cell is currently processing a tick
    - remaining_work: how much work remains in the current tick
    - substrate_ticks_elapsed: how many substrate ticks have passed
    - ticks_processed: how many physical ticks completed
    """
    i: int
    j: int
    tick_budget: int

    busy: bool = False
    remaining_work: int = 0

    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0

    def start_tick(self) -> None:
        """Start a new physical tick if not already busy."""
        if self.busy:
            return
        self.busy = True
        self.remaining_work = self.tick_budget
        self.ticks_processed += 1

    def work_one_unit(self) -> None:
        """Consume one unit of work on the current physical tick."""
        if not self.busy:
            return
        if self.remaining_work > 0:
            self.remaining_work -= 1
            if self.remaining_work == 0:
                self.busy = False

    def advance_substrate_tick(self) -> None:
        """Advance substrate time for this cell."""
        self.substrate_ticks_elapsed += 1

    @property
    def gamma_eff(self) -> float:
        """Effective time dilation: gamma = T_cell / T_substrate."""
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed


# =========================
# Chunk (local capacity)
# =========================

@dataclass
class Chunk:
    """
    A chunk groups a set of cells and has a local capacity per substrate tick.

    - capacity_per_tick: how many units of work can be done in this chunk per substrate tick
    """
    id: Tuple[int, int]
    cells: List[SampleCell]
    capacity_per_tick: int

    total_capacity_used: int = 0
    ticks_processed_count: int = 0

    def step(self) -> None:
        """
        One substrate tick for this chunk:
        - all cells advance substrate time,
        - busy cells consume work first,
        - remaining capacity is used to start new ticks in idle cells.
        """
        # 1) advance substrate time for all cells
        for cell in self.cells:
            cell.advance_substrate_tick()

        available_capacity = self.capacity_per_tick

        # 2) process busy cells first
        busy_cells = [c for c in self.cells if c.busy]
        random.shuffle(busy_cells)  # avoid ordering artifacts

        for cell in busy_cells:
            if available_capacity <= 0:
                break
            cell.work_one_unit()
            available_capacity -= 1

        # 3) start new ticks in idle cells with remaining capacity
        idle_cells = [c for c in self.cells if not c.busy]
        random.shuffle(idle_cells)

        for cell in idle_cells:
            if available_capacity <= 0:
                break
            # starting a tick costs tick_budget units of work
            if cell.tick_budget <= available_capacity:
                cell.start_tick()
                available_capacity -= cell.tick_budget

        # 4) stats
        used = self.capacity_per_tick - available_capacity
        self.total_capacity_used += used
        self.ticks_processed_count += 1

    @property
    def avg_capacity_used(self) -> float:
        if self.ticks_processed_count == 0:
            return 0.0
        return self.total_capacity_used / self.ticks_processed_count

    @property
    def utilization(self) -> float:
        if self.capacity_per_tick == 0:
            return 0.0
        return (self.avg_capacity_used / self.capacity_per_tick) * 100.0


# =========================
# Simulation
# =========================

class Simulation51c:
    """
    Experiment 51c: space as a grid of sample-entities with local chunk capacity.
    """

    def __init__(
            self,
            grid_size: int = 100,
            chunk_size: int = 10,
            planet_radius: float = 10.0,
            planet_tick_budget: int = 5,
            space_tick_budget: int = 1,
            chunk_capacity: int = 50,
            num_substrate_ticks: int = 20000,
    ):
        self.grid_size = grid_size
        self.chunk_size = chunk_size
        self.planet_radius = planet_radius
        self.planet_tick_budget = planet_tick_budget
        self.space_tick_budget = space_tick_budget
        self.chunk_capacity = chunk_capacity
        self.num_substrate_ticks = num_substrate_ticks

        self.cells: Dict[Tuple[int, int], SampleCell] = {}
        self.chunks: Dict[Tuple[int, int], Chunk] = {}

        self.center = (grid_size // 2, grid_size // 2)

    def setup(self) -> None:
        """
        Create the grid of sample-entities and assign them to chunks.
        Planet = disk of higher tick_budget cells around the center.
        """
        print("Setting up grid and chunks for Experiment 51c...")

        # Create cells
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

                cell = SampleCell(i=i, j=j, tick_budget=tick_budget)
                self.cells[(i, j)] = cell

        # Create chunks
        num_chunks_x = self.grid_size // self.chunk_size
        num_chunks_y = self.grid_size // self.chunk_size

        for cx in range(num_chunks_x):
            for cy in range(num_chunks_y):
                chunk_cells: List[SampleCell] = []
                for i in range(cx * self.chunk_size, (cx + 1) * self.chunk_size):
                    for j in range(cy * self.chunk_size, (cy + 1) * self.chunk_size):
                        if (i, j) in self.cells:
                            chunk_cells.append(self.cells[(i, j)])

                chunk_id = (cx, cy)
                chunk = Chunk(
                    id=chunk_id,
                    cells=chunk_cells,
                    capacity_per_tick=self.chunk_capacity,
                )
                self.chunks[chunk_id] = chunk

        print(f"Grid size: {self.grid_size}x{self.grid_size}")
        print(f"Chunk size: {self.chunk_size}x{self.chunk_size}")
        print(f"Total chunks: {len(self.chunks)}")
        print(f"Planet radius: {self.planet_radius}")
        print(f"Planet tick_budget: {self.planet_tick_budget}")
        print(f"Space tick_budget: {self.space_tick_budget}")
        print(f"Chunk capacity: {self.chunk_capacity}")
        print()

    def run(self) -> None:
        """
        Run the simulation for the configured number of substrate ticks.
        """
        print(f"Running Experiment 51c for {self.num_substrate_ticks} substrate ticks...\n")

        for tick in range(self.num_substrate_ticks):
            # Step each chunk independently (local capacity)
            for chunk in self.chunks.values():
                chunk.step()

            if (tick + 1) % (self.num_substrate_ticks // 10) == 0:
                print(f"  Tick {tick + 1}/{self.num_substrate_ticks}")

        print("\nSimulation complete.\n")

    def measure_radial_gamma(self) -> List[Tuple[float, float, SampleCell]]:
        """
        Measure gamma_eff along a radial line from the center outward.
        We use cells on the +x axis: (cx + r, cy).
        """
        cx, cy = self.center

        # Choose radii that stay within the grid
        max_r = min(cx, self.grid_size - cx - 1)
        radii = [r for r in range(1, max_r, 5)]  # step by 5 for readability

        results: List[Tuple[float, float, SampleCell]] = []

        print("=" * 70)
        print("EXPERIMENT 51c: RADIAL TIME DILATION RESULTS")
        print("=" * 70)
        print()
        print(f"{'r':<8} {'gamma_eff':<10} {'ticks_proc':<12} {'ticks_substrate':<16} {'tick_budget':<12}")
        print("-" * 70)

        for r in radii:
            i = cx + r
            j = cy
            cell = self.cells[(i, j)]
            gamma = cell.gamma_eff
            print(
                f"{r:<8} {gamma:<10.3f} {cell.ticks_processed:<12} {cell.substrate_ticks_elapsed:<16} {cell.tick_budget:<12}")
            results.append((float(r), gamma, cell))

        print()
        return results

    def analyze_gradient(self, results: List[Tuple[float, float, SampleCell]]) -> None:
        """
        Analyze monotonicity and fit to 1/r² for (1 - gamma).
        """
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

        # Monotonicity check
        increases = sum(1 for i in range(len(gammas) - 1) if gammas[i + 1] > gammas[i])
        total_pairs = len(gammas) - 1

        print(f"Monotonic increases: {increases}/{total_pairs}")
        if increases >= total_pairs * 0.7:
            print("[TENTATIVE SUCCESS] gamma_eff tends to increase with distance")
        else:
            print("[WARN] No clear monotonic gradient in gamma_eff(r)")
        print()

        # Fit (1 - gamma) ~ k / r^2
        print("Falloff Pattern Analysis:")
        dilation_depth = 1.0 - gammas
        inv_r2 = 1.0 / (distances ** 2)

        # Avoid division by zero at r=0 (we don't include r=0 anyway)
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
        """
        Visualize gamma(r) and (1 - gamma) vs 1/r².
        """
        if not results:
            print("No results to visualize.")
            return

        distances = np.array([r[0] for r in results], dtype=float)
        gammas = np.array([r[1] for r in results], dtype=float)

        plt.figure(figsize=(12, 5))

        # Plot 1: gamma_eff vs distance
        plt.subplot(1, 2, 1)
        plt.plot(distances, gammas, 'bo-', linewidth=2, markersize=6)
        plt.axhline(y=1.0, color='r', linestyle='--', label='gamma=1.0 (no dilation)')
        plt.xlabel('Distance r from center', fontsize=12)
        plt.ylabel('gamma_eff', fontsize=12)
        plt.title('Emergent Time Dilation vs Distance (Experiment 51c)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim([0, 1.05])

        # Plot 2: (1 - gamma) vs 1/r²
        plt.subplot(1, 2, 2)
        dilation_depth = 1.0 - gammas
        inv_r2 = 1.0 / (distances ** 2)

        plt.plot(inv_r2, dilation_depth, 'rs-', linewidth=2, markersize=6)
        plt.xlabel('1 / r²', fontsize=12)
        plt.ylabel('1 - gamma_eff', fontsize=12)
        plt.title('Dilation Depth vs 1/r²', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('time_dilation_results_51c.png', dpi=150, bbox_inches='tight')
        print("Visualization saved to: time_dilation_results_51c.png\n")
        plt.show()


# =========================
# Main
# =========================

def main():
    print()
    print("=" * 70)
    print(" EXPERIMENT 51c: EMERGENT TIME DILATION IN SAMPLE-ENTITY SPACE")
    print("=" * 70)
    print()
    print("Space is represented as a 2D grid of sample-entities.")
    print("A planet is a cluster of higher-cost cells around the center.")
    print("Each chunk has local capacity; no global scheduler is used.")
    print()

    sim = Simulation51c(
        grid_size=100,
        chunk_size=10,
        planet_radius=10.0,
        planet_tick_budget=5,
        space_tick_budget=1,
        chunk_capacity=50,
        num_substrate_ticks=20000,
    )

    sim.setup()
    sim.run()
    results = sim.measure_radial_gamma()
    sim.analyze_gradient(results)
    sim.visualize(results)

    print("=" * 70)
    print("VERDICT (51c, exploratory)")
    print("=" * 70)
    print()
    print("Look at:")
    print("  - monotonicity and smoothness of gamma_eff(r)")
    print("  - whether (1 - gamma) vs 1/r² shows any coherent pattern")
    print()
    print("This is NOT a proof of gravity, just a probe:")
    print("  - Does a sample-entity space with local capacity")
    print("    produce an emergent time-dilation gradient")
    print("    around a planetary cluster?")
    print()


if __name__ == "__main__":
    main()
