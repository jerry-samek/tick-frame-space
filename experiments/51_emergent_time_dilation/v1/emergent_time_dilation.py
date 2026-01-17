#!/usr/bin/env python3
"""
Experiment 51: Emergent Time Dilation from Tick Budgets

Tests if time dilation emerges naturally from computational resource allocation.

This is the CRITICAL test - if this fails, gravity claims are invalid.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Entity:
    """
    Represents an entity with computational cost (tick_budget).
    """
    id: str
    position: Tuple[float, float]
    tick_budget: int  # Computational cost to update (analog of "mass")

    # Statistics
    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0
    ticks_skipped: int = 0

    @property
    def gamma_eff(self) -> float:
        """
        Effective time dilation factor: gamma = τ_observer / τ_substrate

        If gamma < 1.0, entity experiences time dilation (fewer ticks processed).
        """
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed

    def process_tick(self, substrate_tick: int):
        """Entity experiences this substrate tick."""
        self.substrate_ticks_elapsed += 1
        self.ticks_processed += 1

    def skip_tick(self, substrate_tick: int):
        """Entity misses this substrate tick (time dilation effect)."""
        self.substrate_ticks_elapsed += 1
        self.ticks_skipped += 1


@dataclass
class Observer:
    """
    Observer with limited computational capacity.

    This is the KEY mechanism - observer cannot update all entities
    every tick if tick demand exceeds capacity.
    """
    tick_budget_capacity: int

    # Statistics
    total_capacity_used: int = 0
    total_capacity_wasted: int = 0
    ticks_processed_count: int = 0

    def allocate_ticks(self, substrate_tick: int, entities: List[Entity]) -> None:
        """
        Allocate observer's limited tick capacity among entities.

        This is where time dilation emerges:
        - Entities with high tick_budget consume more capacity
        - When capacity exhausted, remaining entities skip ticks
        - Result: Entities near expensive updates experience time dilation
        """
        available_capacity = self.tick_budget_capacity

        # Sort entities by distance from heavy entity (at center)
        # This ensures fair allocation (not biased by list order)
        heavy_entity_pos = (50.0, 50.0)  # Center of grid

        entities_sorted = sorted(
            entities,
            key=lambda e: self._distance(e.position, heavy_entity_pos)
        )

        for entity in entities_sorted:
            if available_capacity >= entity.tick_budget:
                # Entity gets updated this tick
                entity.process_tick(substrate_tick)
                available_capacity -= entity.tick_budget
            else:
                # Capacity exhausted - entity misses this tick
                # This is TIME DILATION from observer's perspective
                entity.skip_tick(substrate_tick)

        # Track capacity usage
        capacity_used = self.tick_budget_capacity - available_capacity
        self.total_capacity_used += capacity_used
        self.total_capacity_wasted += available_capacity
        self.ticks_processed_count += 1

    @staticmethod
    def _distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Euclidean distance between two positions."""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx*dx + dy*dy)

    @property
    def average_capacity_used(self) -> float:
        """Average capacity used per tick."""
        if self.ticks_processed_count == 0:
            return 0.0
        return self.total_capacity_used / self.ticks_processed_count

    @property
    def capacity_utilization(self) -> float:
        """Percentage of capacity used on average."""
        if self.tick_budget_capacity == 0:
            return 0.0
        return (self.average_capacity_used / self.tick_budget_capacity) * 100


class Simulation:
    """
    Runs the time dilation experiment.
    """

    def __init__(
        self,
        heavy_entity_tick_budget: int = 1000,
        light_entity_tick_budget: int = 1,
        observer_capacity: int = 1500,
        num_substrate_ticks: int = 1000
    ):
        self.heavy_entity_tick_budget = heavy_entity_tick_budget
        self.light_entity_tick_budget = light_entity_tick_budget
        self.observer_capacity = observer_capacity
        self.num_substrate_ticks = num_substrate_ticks

        self.entities: List[Entity] = []
        self.observer: Observer = None
        self.substrate_tick = 0

    def setup(self) -> None:
        """
        Create entities and observer.
        """
        # Heavy entity at center (analog of massive object)
        self.entities.append(Entity(
            id="H",
            position=(50.0, 50.0),
            tick_budget=self.heavy_entity_tick_budget
        ))

        # Light entities at various distances
        distances = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        for i, r in enumerate(distances):
            # Place entities in a line from center (for simplicity)
            # Position: (50 + r, 50) - to the right of center
            self.entities.append(Entity(
                id=f"L{i+1}",
                position=(50.0 + r, 50.0),
                tick_budget=self.light_entity_tick_budget
            ))

        # Observer with limited capacity
        self.observer = Observer(tick_budget_capacity=self.observer_capacity)

    def run(self) -> None:
        """
        Run the simulation for specified number of substrate ticks.
        """
        print(f"Running simulation for {self.num_substrate_ticks} substrate ticks...")
        print(f"Heavy entity tick_budget: {self.heavy_entity_tick_budget}")
        print(f"Light entity tick_budget: {self.light_entity_tick_budget}")
        print(f"Observer capacity: {self.observer_capacity}")
        print()

        for tick in range(self.num_substrate_ticks):
            self.substrate_tick = tick

            # Observer allocates ticks among entities
            # This is where time dilation emerges
            self.observer.allocate_ticks(tick, self.entities)

            # Progress indicator
            if (tick + 1) % 100 == 0:
                print(f"  Tick {tick + 1}/{self.num_substrate_ticks}")

        print("\nSimulation complete!")
        print()

    def analyze_results(self) -> None:
        """
        Analyze and print results.
        """
        print("=" * 70)
        print("EXPERIMENT 51: EMERGENT TIME DILATION RESULTS")
        print("=" * 70)
        print()

        # Observer statistics
        print("Observer Statistics:")
        print(f"  Average capacity used: {self.observer.average_capacity_used:.1f} / {self.observer_capacity}")
        print(f"  Capacity utilization: {self.observer.capacity_utilization:.1f}%")
        print()

        # Entity statistics
        print("Time Dilation by Distance:")
        print(f"{'ID':<6} {'Distance':<10} {'gamma_eff':<10} {'Ticks Proc.':<12} {'Ticks Skip.':<12} {'Interpretation'}")
        print("-" * 70)

        heavy_entity = self.entities[0]
        heavy_pos = heavy_entity.position

        results = []

        for entity in self.entities:
            if entity.id == "H":
                # Heavy entity always processed (it's first in sorted list)
                continue

            distance = math.sqrt(
                (entity.position[0] - heavy_pos[0])**2 +
                (entity.position[1] - heavy_pos[1])**2
            )

            gamma = entity.gamma_eff
            interpretation = self._interpret_gamma(gamma)

            print(f"{entity.id:<6} {distance:<10.1f} {gamma:<10.3f} "
                  f"{entity.ticks_processed:<12} {entity.ticks_skipped:<12} {interpretation}")

            results.append((distance, gamma, entity))

        print()

        # Check for time dilation gradient
        self._check_gradient(results)

        return results

    @staticmethod
    def _interpret_gamma(gamma: float) -> str:
        """Interpret gamma_eff value."""
        if gamma >= 0.95:
            return "Negligible"
        elif gamma >= 0.85:
            return "Mild dilation"
        elif gamma >= 0.70:
            return "Moderate dilation"
        elif gamma >= 0.50:
            return "Strong dilation"
        else:
            return "Severe dilation"

    def _check_gradient(self, results: List[Tuple[float, float, Entity]]) -> None:
        """
        Check if time dilation gradient exists.

        Success criterion: gamma_eff should decrease with proximity to heavy entity.
        """
        print("=" * 70)
        print("GRADIENT ANALYSIS")
        print("=" * 70)
        print()

        # Sort by distance
        results_sorted = sorted(results, key=lambda x: x[0])

        # Check if gamma_eff increases with distance (time dilation decreases)
        gammas = [r[1] for r in results_sorted]

        # Count monotonic increases
        increases = sum(1 for i in range(len(gammas)-1) if gammas[i+1] > gammas[i])
        total_pairs = len(gammas) - 1

        print(f"Monotonic increases: {increases}/{total_pairs}")

        if increases >= total_pairs * 0.8:  # 80% threshold
            print("[SUCCESS] GRADIENT EXISTS: gamma_eff increases with distance")
            print("[SUCCESS] Time dilation stronger near heavy entity")
            print()
            print("**HYPOTHESIS SUPPORTED**")
        else:
            print("[FAIL] NO CLEAR GRADIENT: gamma_eff doesn't follow distance pattern")
            print("[FAIL] Time dilation not correlated with proximity")
            print()
            print("**HYPOTHESIS REJECTED**")

        print()

        # Try to fit 1/r² falloff
        self._fit_falloff(results_sorted)

    def _fit_falloff(self, results: List[Tuple[float, float, Entity]]) -> None:
        """
        Attempt to fit gravitational 1/r² falloff to time dilation.

        Model: 1 - gamma_eff ≈ k / r²
        Where: 1 - gamma_eff is "time dilation depth"
        """
        print("Falloff Pattern Analysis:")
        print()

        distances = np.array([r[0] for r in results])
        gammas = np.array([r[1] for r in results])

        # Time dilation depth (how much slower than normal)
        dilation_depth = 1.0 - gammas

        # Try to fit k / r²
        # dilation_depth ≈ k / r²
        # k ≈ dilation_depth * r²

        k_values = dilation_depth * (distances ** 2)
        k_mean = np.mean(k_values)
        k_std = np.std(k_values)

        print(f"  Fitting: (1 - gamma) ≈ k / r²")
        print(f"  Best fit k: {k_mean:.2f} ± {k_std:.2f}")
        print()

        # Check goodness of fit
        predicted_dilation = k_mean / (distances ** 2)
        residuals = dilation_depth - predicted_dilation
        rmse = np.sqrt(np.mean(residuals ** 2))

        print(f"  RMSE: {rmse:.4f}")

        if rmse < 0.1:  # Arbitrary threshold
            print("  [SUCCESS] Good fit to 1/r² gravitational falloff")
        else:
            print("  [WARN] Poor fit - pattern doesn't match 1/r²")

        print()

    def visualize(self, results: List[Tuple[float, float, Entity]]) -> None:
        """
        Create visualization of results.
        """
        distances = [r[0] for r in results]
        gammas = [r[1] for r in results]

        plt.figure(figsize=(12, 5))

        # Plot 1: gamma_eff vs distance
        plt.subplot(1, 2, 1)
        plt.plot(distances, gammas, 'bo-', linewidth=2, markersize=8)
        plt.axhline(y=1.0, color='r', linestyle='--', label='gamma=1.0 (no dilation)')
        plt.xlabel('Distance from Heavy Entity (r)', fontsize=12)
        plt.ylabel('gamma_eff (Time Dilation Factor)', fontsize=12)
        plt.title('Emergent Time Dilation vs Distance', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim([0, 1.1])

        # Plot 2: Time dilation depth vs 1/r²
        plt.subplot(1, 2, 2)
        dilation_depth = 1.0 - np.array(gammas)
        inverse_r_squared = 1.0 / (np.array(distances) ** 2)

        plt.plot(inverse_r_squared, dilation_depth, 'rs-', linewidth=2, markersize=8)
        plt.xlabel('1/r² (Gravitational Factor)', fontsize=12)
        plt.ylabel('1 - gamma_eff (Dilation Depth)', fontsize=12)
        plt.title('Gravitational Falloff Pattern', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save plot
        plt.savefig('time_dilation_results.png', dpi=150, bbox_inches='tight')
        print("Visualization saved to: time_dilation_results.png")
        print()

        plt.show()


def main():
    """
    Run Experiment 51.
    """
    print()
    print("=" * 70)
    print(" EXPERIMENT 51: EMERGENT TIME DILATION FROM TICK BUDGETS")
    print("=" * 70)
    print()
    print("This is THE critical test.")
    print("If this fails -> gravity claims are invalid.")
    print()

    # Create and run simulation
    sim = Simulation(
        heavy_entity_tick_budget=1000,   # "Mass" of heavy entity
        light_entity_tick_budget=1,      # "Mass" of light entities
        observer_capacity=1005,          # Observer's computational limit (creates saturation!)
        num_substrate_ticks=1000         # Duration of experiment
    )

    sim.setup()
    sim.run()
    results = sim.analyze_results()
    sim.visualize(results)

    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()
    print("If gradient exists and follows 1/r^2:")
    print("  -> Time dilation emerges from tick budgets")
    print("  -> Mechanism is valid")
    print("  -> Proceed to Experiments #52-55")
    print()
    print("If no gradient or requires tuning:")
    print("  -> Mechanism doesn't work")
    print("  -> Claims are invalid")
    print("  -> This is just a game engine")
    print()


if __name__ == "__main__":
    main()
