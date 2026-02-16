"""Measure PEAK gamma at entity position as a function of mass.

The hypothesis: energy = peak gamma at the entity's node, not total field integral.

An entity with mass M sits at a node for M ticks, depositing 1.0 per tick.
Each tick, the field also spreads (losing 1/k per neighbor) and decays (0.9999).

Order of operations per tick:
1. spread_all (spread + decay)
2. entity deposits

Peak gamma after M ticks of sitting:
  gamma(t) = sum_{i=0}^{t-1} d * r^i = d * (1 - r^t) / (1 - r)
  where r = retention per tick = (1 - alpha) * decay
  alpha = spread_fraction = 1/k
  d = deposit_amount = 1.0

For k=6, decay=0.9999:
  r = (1 - 1/6) * 0.9999 = 5/6 * 0.9999 = 0.83325
  gamma(M) = 1.0 * (1 - 0.83325^M) / (1 - 0.83325)

This is the analytical prediction. We also run the actual simulation to verify.
"""

import numpy as np
import sys
import os

# Add v5 directory to path so we can import the simulation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

masses = [1, 2, 3, 5, 10, 20, 50, 100]
k = 6
decay = 0.9999
deposit_amount = 1.0
alpha = 1.0 / k  # spread_fraction

# Retention at the peak node per tick (after spread and decay, before new deposit)
# The spread matrix diagonal = (1-alpha), then multiply by decay
r = (1.0 - alpha) * decay
print(f"Parameters: k={k}, decay={decay}, alpha={alpha:.4f}")
print(f"Retention per tick: r = (1-alpha)*decay = {r:.6f}")
print(f"Loss per tick: 1-r = {1-r:.6f}")
print(f"Steady-state (infinite M): gamma_inf = d/(1-r) = {deposit_amount/(1-r):.2f}")
print()

# Analytical prediction
print("=" * 90)
print("ANALYTICAL PREDICTION: gamma_peak(M) = d * (1 - r^M) / (1 - r)")
print("=" * 90)
print()
print(f"{'Mass':>5} | {'Peak gamma':>12} | {'mc (c=1)':>8} | {'mc^2':>8} | {'peak/m':>8} | {'peak/m^2':>8} | {'peak*v':>8} | {'peak*v^2':>10}")
print("-" * 95)

analytical = {}
for M in masses:
    peak = deposit_amount * (1.0 - r**M) / (1.0 - r)
    v = 1.0 / M  # c/M
    analytical[M] = peak
    print(f"{M:5d} | {peak:12.4f} | {M:8.1f} | {M:8.1f} | {peak/M:8.4f} | {peak/M**2:8.6f} | {peak*v:8.4f} | {peak*v**2:10.6f}")

print()

# Key ratios
print("=" * 90)
print("SCALING: peak_gamma(M) / peak_gamma(1)")
print("=" * 90)
print()
p1 = analytical[1]
print(f"{'Mass':>5} | {'Peak':>10} | {'Ratio':>8} | {'M':>5} | {'M^2':>6} | {'log(M)':>8} | {'1-r^M':>10}")
print("-" * 70)
for M in masses:
    p = analytical[M]
    ratio = p / p1
    print(f"{M:5d} | {p:10.4f} | {ratio:8.4f} | {M:5d} | {M**2:6d} | {np.log(M):8.3f} | {1-r**M:10.6f}")

# The ratio is (1 - r^M) / (1 - r^1) = (1 - r^M) / (1 - r)
# For small M: approximately M (linear) because r^M ~ 1 - M*ln(1/r) ~ 1 - M*(1-r)
# For large M: saturates at 1/(1-r) / (1/(1-r)) = approaches 1/(1-r^1)
# Actually: ratio = (1 - r^M) / (1 - r)
# Let's check if this is ever proportional to M

print()
print("=" * 90)
print("IS PEAK GAMMA PROPORTIONAL TO M FOR SMALL M?")
print("=" * 90)
print()
print("For small M, using Taylor expansion:")
print(f"  r = {r:.6f}")
print(f"  -ln(r) = {-np.log(r):.6f}")
print(f"  1-r = {1-r:.6f}")
print()
print("  r^M = exp(M * ln(r)) = exp(-M * {:.6f})".format(-np.log(r)))
print("  1 - r^M ~ M * (-ln(r)) for small M")
print("  peak(M) ~ d * M * (-ln(r)) / (1-r)")
print(f"  ~ d * M * {-np.log(r)/(1-r):.4f}")
print()
print("So for small M, peak IS approximately proportional to M!")
print(f"Proportionality constant: {-np.log(r)/(1-r):.6f}")
print(f"Which equals: -ln(r)/(1-r) = {-np.log(r)/(1-r):.6f}")
print(f"For r close to 1: -ln(r)/(1-r) -> 1 (L'Hopital)")
print(f"Our r={r:.6f} gives ratio = {-np.log(r)/(1-r):.6f}")
print()

# Verify with actual ratio
print("Verification: peak(M) / M for each mass:")
for M in masses:
    p = analytical[M]
    print(f"  M={M:3d}: peak/M = {p/M:.6f}, expected ~{deposit_amount * (-np.log(r)) / (1-r):.6f}")

# Now the big question: is peak gamma = mc^2 in some sense?
# With c=1 (natural units), mc^2 = m.
# Peak gamma IS approximately M for small M.
# For large M, it saturates at d/(1-r).
#
# But what if c is NOT 1? What if c relates to the retention r somehow?
# c = 1 hop/tick is the field propagation speed.
# In the spread matrix, alpha = 1/k gives ~1 hop/tick propagation.
# The SPEED of the field front is c.
# The STRENGTH of the field at 1 hop after 1 tick is alpha * decay.
#
# What if we define c_eff = alpha * decay = (1/k) * 0.9999?
# Then retention r = 1 - c_eff = 1 - alpha*decay
# No, that's not right either. r = (1-alpha)*decay.

print()
print("=" * 90)
print("WHAT IF c IS NOT 1?")
print("=" * 90)
print()
print("The field propagation speed c = 1 hop/tick.")
print("But the field AMPLITUDE reaching the next node per tick is alpha = 1/k.")
print()
print("If we define an 'amplitude speed' c_amp = alpha * decay = {:.6f}".format(alpha * decay))
print("Then the 'amplitude c^2' = {:.6f}".format((alpha * decay)**2))
print()

c_amp = alpha * decay
print(f"Test: peak(M) vs M * c_amp^2 = M * {c_amp**2:.6f}")
print()
for M in masses:
    p = analytical[M]
    expected = M * c_amp**2
    print(f"  M={M:3d}: peak={p:.4f}, M*c_amp^2={expected:.6f}, ratio={p/expected:.2f}")

print()
print(f"Test: peak(M) vs M * c_amp = M * {c_amp:.6f}")
print()
for M in masses:
    p = analytical[M]
    expected = M * c_amp
    print(f"  M={M:3d}: peak={p:.4f}, M*c_amp={expected:.6f}, ratio={p/expected:.2f}")

# But wait - there's ALSO the incoming gamma from neighbors.
# The analytical model above assumes the entity's node ONLY gets direct deposits.
# In reality, neighbor nodes also have some gamma (from previous spread),
# and they spread some back. This increases the effective retention.
#
# Let's run a quick simulation to get the TRUE peak gamma.

print()
print("=" * 90)
print("SIMULATION: True peak gamma on actual lattice graph")
print("=" * 90)
print()

try:
    from three_body_graph import GammaFieldGraph
    import networkx as nx

    # Build a small lattice graph (same as experiment)
    side = 15  # smaller for speed
    G = nx.grid_graph(dim=[side, side, side])
    G = nx.convert_node_labels_to_integers(G)
    n_nodes = G.number_of_nodes()

    fg = GammaFieldGraph(G, spread_fraction=1.0/k, decay=decay)
    fg.add_field("entity")

    center = n_nodes // 2  # entity sits at center

    print(f"Lattice: {side}^3 = {n_nodes} nodes, k={k}")
    print()

    for M in [1, 2, 3, 5, 10, 20, 50]:
        # Reset field
        fg.fields["entity"] = np.zeros(n_nodes, dtype=np.float64)

        # Simulate: entity sits at center for M ticks
        # Each tick: spread_all, then deposit
        for tick in range(M):
            fg.spread_all()
            fg.deposit("entity", center, deposit_amount)

        peak_sim = fg.fields["entity"][center]
        peak_ana = analytical[M]

        # Also measure total field
        total_sim = float(np.sum(fg.fields["entity"]))

        print(f"  M={M:3d}: peak_sim={peak_sim:.4f}, peak_analytical={peak_ana:.4f}, "
              f"ratio_sim/ana={peak_sim/peak_ana:.4f}, total_field={total_sim:.2f}")

    # Now do longer runs - entity deposits for many cycles
    # to reach true steady state (deposit M ticks, move, deposit M ticks, ...)
    print()
    print("STEADY STATE: many deposit-move cycles (200 cycles)")
    print()

    for M in [1, 2, 3, 5, 10, 20]:
        fg.fields["entity"] = np.zeros(n_nodes, dtype=np.float64)

        # Start entity at center, simulate 200 move cycles
        node = center
        prev_node = center
        peaks = []

        for cycle in range(200):
            # Sit for M ticks
            for tick in range(M):
                fg.spread_all()
                # Mass-conserving: withdraw from prev, deposit at current
                available = fg.fields["entity"][prev_node]
                withdraw = min(deposit_amount, available)
                fg.fields["entity"][prev_node] -= withdraw
                fg.deposit("entity", node, deposit_amount)

            # Record peak at entity position
            peaks.append(fg.fields["entity"][node])

            # Move to a random neighbor (simulating hop)
            prev_node = node
            nbs = list(G.neighbors(node))
            node = nbs[np.random.randint(len(nbs))]

        ss_peak = np.mean(peaks[-50:])  # last 50 cycles
        total = float(np.sum(fg.fields["entity"]))
        print(f"  M={M:3d}: ss_peak={ss_peak:.4f}, total_field={total:.2f}, "
              f"peak/M={ss_peak/M:.4f}, peak/M^2={ss_peak/M**2:.6f}")

except ImportError as e:
    print(f"Could not import simulation: {e}")
    print("Running analytical only.")
