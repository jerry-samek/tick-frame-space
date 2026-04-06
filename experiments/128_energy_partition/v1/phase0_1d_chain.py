#!/usr/bin/env python3
"""
Experiment 128 v1 — Phase 0: 1D Connector Chain

The simplest possible test. A chain of connectors between "star" (left)
and "planet" (right). No graph. No hopping. No routing.

Each tick:
  - Star deposits one quantum at its end (rightward propagation)
  - Planet deposits one quantum at its end (leftward propagation)
  - Deposits propagate at c=1 connector/tick
  - Where they meet: Same consumes Different

Track: boundary position over time, deposit density profile,
consumption rate, equilibrium.

The entity IS the region where its deposits dominate. Movement IS
the boundary shifting.
"""

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Configuration ──────────────────────────────────────────────
N_CONNECTORS = 100      # chain length
STAR_RATE = 1            # star deposits per tick
PLANET_RATE = 1           # planet deposits per tick
TICKS = 10000
MEASURE_EVERY = 100

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class Connector:
    """A connector in the 1D chain with Same/Different/consumption."""

    __slots__ = ('star_deposits', 'planet_deposits', 'different_count',
                 'consumed_count')

    def __init__(self):
        self.star_deposits = 0
        self.planet_deposits = 0
        self.different_count = 0
        self.consumed_count = 0

    @property
    def dominant(self):
        if self.star_deposits > self.planet_deposits:
            return 'star'
        elif self.planet_deposits > self.star_deposits:
            return 'planet'
        return None

    @property
    def total(self):
        return self.star_deposits + self.planet_deposits

    def deposit_star(self):
        """Star deposits. If star-dominant: Same (consume one Different).
        If planet-dominant: Different (extend)."""
        self.star_deposits += 1
        dom = self.dominant
        if dom == 'star' or dom is None:
            # Same or first deposit
            if self.different_count > 0:
                self.different_count -= 1
                self.consumed_count += 1
        else:
            # Different (planet-dominant connector receives star deposit)
            self.different_count += 1

    def deposit_planet(self):
        """Planet deposits. Same logic, reversed."""
        self.planet_deposits += 1
        dom = self.dominant
        if dom == 'planet' or dom is None:
            if self.different_count > 0:
                self.different_count -= 1
                self.consumed_count += 1
        else:
            self.different_count += 1


class Quantum:
    """A propagating deposit quantum on the 1D chain."""
    __slots__ = ('family', 'position', 'direction')

    def __init__(self, family, position, direction):
        self.family = family      # 'star' or 'planet'
        self.position = position  # connector index
        self.direction = direction  # +1 (rightward) or -1 (leftward)


def find_boundary(chain):
    """Find the boundary position: rightmost star-dominant connector."""
    boundary = 0
    for i, c in enumerate(chain):
        if c.star_deposits >= c.planet_deposits and c.total > 0:
            boundary = i
    return boundary


def density_profile(chain):
    """Return star and planet deposit counts per connector."""
    star = [c.star_deposits for c in chain]
    planet = [c.planet_deposits for c in chain]
    return star, planet


def run():
    print(f"Phase 0: 1D Chain ({N_CONNECTORS} connectors, {TICKS} ticks)")
    print(f"Star rate={STAR_RATE}/tick (rightward), Planet rate={PLANET_RATE}/tick (leftward)")

    chain = [Connector() for _ in range(N_CONNECTORS)]
    quanta = []

    rows = []
    snapshots = {}  # tick -> (star_profile, planet_profile)

    for tick in range(1, TICKS + 1):
        # Star emits from left end (position 0, rightward)
        for _ in range(STAR_RATE):
            quanta.append(Quantum('star', 0, +1))

        # Planet emits from right end (position N-1, leftward)
        for _ in range(PLANET_RATE):
            quanta.append(Quantum('planet', N_CONNECTORS - 1, -1))

        # Propagate all quanta and deposit
        surviving = []
        for q in quanta:
            # Deposit on current connector
            if 0 <= q.position < N_CONNECTORS:
                if q.family == 'star':
                    chain[q.position].deposit_star()
                else:
                    chain[q.position].deposit_planet()

            # Advance
            q.position += q.direction

            # Still in bounds?
            if 0 <= q.position < N_CONNECTORS:
                surviving.append(q)
            # else: quantum exits the chain — gone

        quanta = surviving

        if tick % MEASURE_EVERY == 0:
            boundary = find_boundary(chain)
            total_consumed = sum(c.consumed_count for c in chain)
            total_different = sum(c.different_count for c in chain)
            total_star = sum(c.star_deposits for c in chain)
            total_planet = sum(c.planet_deposits for c in chain)
            active_quanta = len(quanta)

            rows.append({
                'tick': tick,
                'boundary': boundary,
                'total_star': total_star,
                'total_planet': total_planet,
                'total_consumed': total_consumed,
                'total_different': total_different,
                'active_quanta': active_quanta,
            })

            if tick in (100, 500, 1000, 2000, 5000, 10000):
                s, p = density_profile(chain)
                snapshots[tick] = (s, p)

            if tick % 1000 == 0:
                print(f"  t={tick:6d}  boundary={boundary:3d}  "
                      f"star={total_star}  planet={total_planet}  "
                      f"consumed={total_consumed}  diff={total_different}  "
                      f"quanta={active_quanta}")

    print(f"\nDone: {TICKS} ticks")

    analyze(rows, chain)
    plot(rows, snapshots, chain)


def analyze(rows, chain):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # Boundary position
    boundaries = [r['boundary'] for r in rows]
    late = [r for r in rows if r['tick'] > TICKS * 0.5]
    if late:
        mean_b = np.mean([r['boundary'] for r in late])
        std_b = np.std([r['boundary'] for r in late])
        print(f"  Boundary position (late): mean={mean_b:.1f}  std={std_b:.1f}")
        print(f"  Expected equilibrium: {N_CONNECTORS // 2} (middle, equal rates)")

    # Consumption
    final = rows[-1]
    print(f"  Total consumed: {final['total_consumed']}")
    print(f"  Total different: {final['total_different']}")
    print(f"  Total star deposits: {final['total_star']}")
    print(f"  Total planet deposits: {final['total_planet']}")

    # Boundary stability
    if late:
        oscillates = std_b > 1.0
        print(f"  Boundary oscillates: {'YES' if oscillates else 'NO'} (std={std_b:.1f})")

    # Conservation: star_deposited + planet_deposited = still_in_chain + consumed + exited
    total_deposited = STAR_RATE * TICKS + PLANET_RATE * TICKS
    still_in = sum(c.total for c in chain)
    consumed = final['total_consumed']
    print(f"  Deposited: {total_deposited}  In chain: {still_in}  "
          f"Consumed: {consumed}  Exited: {total_deposited - still_in}")

    print()


def plot(rows, snapshots, chain):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Experiment 128 v1 -- Phase 0: 1D Chain', fontsize=14)

    # 1. Boundary position over time
    ax = axes[0, 0]
    ax.plot(ticks, [r['boundary'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(N_CONNECTORS / 2, color='r', linestyle='--', alpha=0.5,
               label=f'midpoint={N_CONNECTORS//2}')
    ax.set_ylabel('Boundary position')
    ax.set_title('Entity Boundary (star-dominant rightmost)')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 2. Deposit profiles at select ticks
    ax = axes[0, 1]
    colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
    for (t, (s, p)), c in zip(sorted(snapshots.items()), colors):
        x = range(N_CONNECTORS)
        net = [s[i] - p[i] for i in range(N_CONNECTORS)]
        ax.plot(x, net, '-', color=c, linewidth=0.8, label=f't={t}')
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_xlabel('Connector position')
    ax.set_ylabel('Star deposits - Planet deposits')
    ax.set_title('Net Deposit Profile (+ = star dominant)')
    ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

    # 3. Star vs planet total deposits
    ax = axes[1, 0]
    ax.plot(ticks, [r['total_star'] for r in rows], 'orange', linewidth=0.8, label='Star')
    ax.plot(ticks, [r['total_planet'] for r in rows], 'blue', linewidth=0.8, label='Planet')
    ax.set_ylabel('Total deposits')
    ax.set_title('Cumulative Deposits')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 4. Consumed over time
    ax = axes[1, 1]
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'green', linewidth=0.8)
    ax.set_ylabel('Consumed')
    ax.set_title('Cumulative Consumption (Different -> Same)')
    ax.grid(True, alpha=0.3)

    # 5. Final deposit profile (star and planet separately)
    ax = axes[2, 0]
    s, p = density_profile(chain)
    x = range(N_CONNECTORS)
    ax.fill_between(x, s, alpha=0.5, color='orange', label='Star')
    ax.fill_between(x, [-pi for pi in p], alpha=0.5, color='blue', label='Planet')
    ax.axhline(0, color='k', linewidth=0.5)
    ax.set_xlabel('Connector position')
    ax.set_ylabel('Deposits (star +, planet -)')
    ax.set_title(f'Final Profile (t={TICKS})')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 6. Active quanta over time
    ax = axes[2, 1]
    ax.plot(ticks, [r['active_quanta'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Count')
    ax.set_xlabel('Tick')
    ax.set_title('Active Quanta in Chain')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase0_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
