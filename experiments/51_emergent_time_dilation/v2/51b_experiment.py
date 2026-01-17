#!/usr/bin/env python3
"""
Experiment 51b: Planetary Emergent Time Dilation from Tick Budgets

Varianta Experimentu 51:
- místo jedné těžké entity je "planeta" = shluk mnoha malých entit,
- každá entita má práci, která trvá více substrate ticků (BUSY/IDLE),
- pozorovatel má omezenou kapacitu práce na substrate tick,
- měříme efektivní časovou dilataci γ_eff pro lehké sondy v různých vzdálenostech.

Cíl:
- zjistit, jestli kolektivní výpočetní zátěž planetárního shluku
  vytváří plynulejší gradient γ(r) než původní binární cutoff v 51.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np


# =========================
# Entity model
# =========================

@dataclass
class Entity:
    """
    Entita s tick_budget a stavem BUSY/IDLE.

    - tick_budget: kolik jednotek práce potřebuje na jeden "fyzikální" tick
    - busy: jestli právě "pracuje" (spotřebovává kapacitu, ale neposouvá svůj čas)
    - remaining_work: kolik práce zbývá do dokončení aktuálního fyzikálního ticku
    """
    id: str
    position: Tuple[float, float]
    tick_budget: int

    # statistiky
    substrate_ticks_elapsed: int = 0
    ticks_processed: int = 0
    ticks_skipped: int = 0

    # stav práce
    busy: bool = False
    remaining_work: int = 0

    def start_physical_tick(self):
        """
        Začne nový fyzikální tick (posun vlastního času).
        Tady by se normálně děla fyzika (update stavu).
        """
        if self.busy:
            # nemělo by nastat, ale pro jistotu
            return
        self.busy = True
        self.remaining_work = self.tick_budget
        self.ticks_processed += 1

    def work_one_unit(self):
        """
        Spotřebuje jednu jednotku výpočetní kapacity na rozpracovaném ticku.
        """
        if not self.busy:
            return
        if self.remaining_work > 0:
            self.remaining_work -= 1
            if self.remaining_work == 0:
                self.busy = False

    def mark_skipped(self):
        """
        Substrate tick proběhl, ale entita nedostala nový fyzikální tick.
        """
        self.ticks_skipped += 1

    @property
    def gamma_eff(self) -> float:
        """
        Efektivní časová dilatace: γ = T_entity / T_substrate.
        """
        if self.substrate_ticks_elapsed == 0:
            return 1.0
        return self.ticks_processed / self.substrate_ticks_elapsed


# =========================
# Observer / scheduler
# =========================

@dataclass
class Observer:
    """
    Pozorovatel s omezenou kapacitou práce na substrate tick.

    tick_budget_capacity = kolik jednotek "work" může provést za jeden substrate tick.
    """
    tick_budget_capacity: int

    total_capacity_used: int = 0
    total_capacity_wasted: int = 0
    ticks_processed_count: int = 0

    def allocate_ticks(self, substrate_tick: int, entities: List[Entity]) -> None:
        """
        Jeden substrate tick:

        1) všem entitám přibude substrate tick (substrát běží uniformně),
        2) nejdřív obsloužíme BUSY entity (rozpracovanou práci),
        3) zbylou kapacitu použijeme na start nových fyzikálních ticků u IDLE entit.
        """
        # 1) substrát běží
        for e in entities:
            e.substrate_ticks_elapsed += 1

        available_capacity = self.tick_budget_capacity

        # 2) obsluha BUSY entit
        busy_entities = [e for e in entities if e.busy]

        # jednoduché pořadí – můžeš později nahradit něčím lokálnějším
        for e in busy_entities:
            if available_capacity <= 0:
                break
            e.work_one_unit()
            available_capacity -= 1

        # 3) start nových fyzikálních ticků u IDLE entit
        idle_entities = [e for e in entities if not e.busy]

        # pro férovost náhodně promícháme pořadí
        random.shuffle(idle_entities)

        for e in idle_entities:
            if available_capacity <= 0:
                # tenhle substrate tick entita "viděla", ale nedostala fyzikální tick
                e.mark_skipped()
                continue

            # start nového fyzikálního ticku
            e.start_physical_tick()
            # spotřebujeme tick_budget jednotek práce (u většiny = 1, u planetárních >1)
            work_cost = e.tick_budget
            if work_cost > available_capacity:
                # pokud by to přesáhlo kapacitu, tak tohle kolo raději nespustíme
                # (můžeš změnit podle chování, které chceš)
                e.busy = False
                e.remaining_work = 0
                e.ticks_processed -= 1
                e.mark_skipped()
                continue

            available_capacity -= work_cost

        # 4) statistika pozorovatele
        capacity_used = self.tick_budget_capacity - available_capacity
        self.total_capacity_used += capacity_used
        self.total_capacity_wasted += max(0, available_capacity)
        self.ticks_processed_count += 1

    @property
    def average_capacity_used(self) -> float:
        if self.ticks_processed_count == 0:
            return 0.0
        return self.total_capacity_used / self.ticks_processed_count

    @property
    def capacity_utilization(self) -> float:
        if self.tick_budget_capacity == 0:
            return 0.0
        return (self.average_capacity_used / self.tick_budget_capacity) * 100.0


# =========================
# Simulation
# =========================

class Simulation:
    """
    Experiment 51b: planetární shluk + lehké sondy.
    """

    def __init__(
            self,
            planet_center: Tuple[float, float] = (50.0, 50.0),
            planet_radius: float = 10.0,
            num_planet_entities: int = 5000,
            planet_tick_budget: int = 5,
            light_entity_tick_budget: int = 1,
            observer_capacity: int = 2000,
            num_substrate_ticks: int = 20000,
    ):
        self.planet_center = planet_center
        self.planet_radius = planet_radius
        self.num_planet_entities = num_planet_entities
        self.planet_tick_budget = planet_tick_budget
        self.light_entity_tick_budget = light_entity_tick_budget
        self.observer_capacity = observer_capacity
        self.num_substrate_ticks = num_substrate_ticks

        self.entities: List[Entity] = []
        self.observer: Observer | None = None
        self.substrate_tick: int = 0

    def setup(self) -> None:
        """
        Vytvoří planetární shluk a lehké sondy.
        """
        cx, cy = self.planet_center

        # Planetární shluk: mnoho malých entit s větším tick_budget
        for i in range(self.num_planet_entities):
            # náhodná pozice v disku o poloměru planet_radius
            r = self.planet_radius * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)

            self.entities.append(Entity(
                id=f"P{i}",
                position=(x, y),
                tick_budget=self.planet_tick_budget,
            ))

        # Lehké sondy v různých vzdálenostech od středu planety
        distances = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70]

        for i, r in enumerate(distances):
            x = cx + r
            y = cy
            self.entities.append(Entity(
                id=f"L{i+1}",
                position=(x, y),
                tick_budget=self.light_entity_tick_budget,
            ))

        # Pozorovatel
        self.observer = Observer(tick_budget_capacity=self.observer_capacity)

    def run(self) -> None:
        """
        Spustí simulaci.
        """
        print(f"Running Experiment 51b for {self.num_substrate_ticks} substrate ticks...")
        print(f"Planet: {self.num_planet_entities} entities, radius={self.planet_radius}, tick_budget={self.planet_tick_budget}")
        print(f"Light entities tick_budget: {self.light_entity_tick_budget}")
        print(f"Observer capacity: {self.observer_capacity}")
        print()

        for tick in range(self.num_substrate_ticks):
            self.substrate_tick = tick
            self.observer.allocate_ticks(tick, self.entities)

            if (tick + 1) % (self.num_substrate_ticks // 10) == 0:
                print(f"  Tick {tick + 1}/{self.num_substrate_ticks}")

        print("\nSimulation complete!\n")

    def analyze_results(self):
        """
        Vypíše výsledky pro lehké sondy a zkusí najít gradient γ(r).
        """
        print("=" * 70)
        print("EXPERIMENT 51b: PLANETARY TIME DILATION RESULTS")
        print("=" * 70)
        print()

        # Observer statistics
        print("Observer Statistics:")
        print(f"  Average capacity used: {self.observer.average_capacity_used:.1f} / {self.observer_capacity}")
        print(f"  Capacity utilization: {self.observer.capacity_utilization:.1f}%")
        print()

        # Planet center
        cx, cy = self.planet_center

        # Collect results for light entities
        results = []
        print("Time Dilation by Distance (Light Probes):")
        print(f"{'ID':<6} {'Distance':<10} {'gamma_eff':<10} {'Ticks Proc.':<12} {'Ticks Skip.':<12}")
        print("-" * 70)

        for e in self.entities:
            if not e.id.startswith("L"):
                continue
            dx = e.position[0] - cx
            dy = e.position[1] - cy
            dist = math.sqrt(dx*dx + dy*dy)
            gamma = e.gamma_eff
            print(f"{e.id:<6} {dist:<10.1f} {gamma:<10.3f} {e.ticks_processed:<12} {e.ticks_skipped:<12}")
            results.append((dist, gamma, e))

        print()
        self._check_gradient(results)
        return results

    def _check_gradient(self, results: List[Tuple[float, float, Entity]]) -> None:
        """
        Zkusí zjistit, jestli γ_eff roste s vzdáleností (plynulý gradient).
        """
        print("=" * 70)
        print("GRADIENT ANALYSIS")
        print("=" * 70)
        print()

        if not results:
            print("No light entities found.")
            return

        results_sorted = sorted(results, key=lambda x: x[0])
        distances = [r[0] for r in results_sorted]
        gammas = [r[1] for r in results_sorted]

        increases = sum(1 for i in range(len(gammas) - 1) if gammas[i+1] > gammas[i])
        total_pairs = len(gammas) - 1

        print(f"Monotonic increases: {increases}/{total_pairs}")
        if increases >= total_pairs * 0.7:
            print("[TENTATIVE SUCCESS] γ_eff tends to increase with distance")
        else:
            print("[WARN] No clear monotonic gradient in γ_eff(r)")

        print()
        self._fit_falloff(distances, gammas)

    def _fit_falloff(self, distances: List[float], gammas: List[float]) -> None:
        """
        Zkusí fitnout (1 - γ) ≈ k / r².
        """
        print("Falloff Pattern Analysis:")
        print()

        distances_arr = np.array(distances)
        gammas_arr = np.array(gammas)

        dilation_depth = 1.0 - gammas_arr
        k_values = dilation_depth * (distances_arr ** 2)
        k_mean = np.mean(k_values)
        k_std = np.std(k_values)

        print(f"  Fitting: (1 - gamma) ≈ k / r²")
        print(f"  Best fit k: {k_mean:.4f} ± {k_std:.4f}")

        predicted_dilation = k_mean / (distances_arr ** 2)
        residuals = dilation_depth - predicted_dilation
        rmse = np.sqrt(np.mean(residuals ** 2))

        print(f"  RMSE: {rmse:.4f}")
        if rmse < 0.05:
            print("  [TENTATIVE SUCCESS] Reasonable fit to 1/r² falloff")
        else:
            print("  [WARN] Poor fit to 1/r² pattern")

        print()

    def visualize(self, results: List[Tuple[float, float, Entity]]) -> None:
        """
        Vizualizace γ(r) a (1 - γ) vs 1/r².
        """
        distances = [r[0] for r in results]
        gammas = [r[1] for r in results]

        plt.figure(figsize=(12, 5))

        # Plot 1: gamma_eff vs distance
        plt.subplot(1, 2, 1)
        plt.plot(distances, gammas, 'bo-', linewidth=2, markersize=8)
        plt.axhline(y=1.0, color='r', linestyle='--', label='gamma=1.0 (no dilation)')
        plt.xlabel('Distance from Planet Center (r)', fontsize=12)
        plt.ylabel('gamma_eff (Time Dilation Factor)', fontsize=12)
        plt.title('Emergent Time Dilation vs Distance', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim([0, 1.05])

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
        plt.savefig('time_dilation_results_51b.png', dpi=150, bbox_inches='tight')
        print("Visualization saved to: time_dilation_results_51b.png\n")
        plt.show()


# =========================
# Main
# =========================

def main():
    print()
    print("=" * 70)
    print(" EXPERIMENT 51b: PLANETARY EMERGENT TIME DILATION")
    print("=" * 70)
    print()
    print("Variant of Experiment 51 with:")
    print("  - planetary cluster of many small entities")
    print("  - BUSY/IDLE work over multiple substrate ticks")
    print("  - limited observer capacity")
    print()

    sim = Simulation(
        planet_center=(50.0, 50.0),
        planet_radius=10.0,
        num_planet_entities=5000,
        planet_tick_budget=5,
        light_entity_tick_budget=1,
        observer_capacity=2000,
        num_substrate_ticks=20000,
    )

    sim.setup()
    sim.run()
    results = sim.analyze_results()
    sim.visualize(results)

    print("=" * 70)
    print("VERDICT (51b, exploratory)")
    print("=" * 70)
    print()
    print("Look at:")
    print("  - monotonicity of gamma_eff(r)")
    print("  - smoothness (no hard step)")
    print("  - approximate 1/r² falloff (if any)")
    print()
    print("This is NOT a proof of gravity, just a probe:")
    print("  - Does a planetary cluster + multi-tick work")
    print("    produce a smoother time-dilation gradient")
    print("    than the original single-entity 51?")
    print()


if __name__ == "__main__":
    main()
