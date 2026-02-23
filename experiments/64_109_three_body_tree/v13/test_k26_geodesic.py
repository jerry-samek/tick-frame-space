"""Quick k=26 geodesic test: does higher connectivity smooth the orbit?

k=6 (cubic lattice) showed bound chaotic orbits with rectangular loops.
k=26 (Moore neighborhood: face + edge + corner neighbors) should smooth
the trajectory into a recognizable ellipse if chaos was a lattice artifact.

Same Schwarzschild edge profile as the k=6 test. Same geodesic frame rotation.
Only difference: 26 directions instead of 6.

Usage:
    python test_k26_geodesic.py [--r-s 10] [--side 40] [--ticks 30000]
"""

import argparse
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# All 26 neighbor offsets in 3D Moore neighborhood
# Face neighbors (6): ±x, ±y, ±z
# Edge neighbors (12): ±x±y, ±x±z, ±y±z
# Corner neighbors (8): ±x±y±z
OFFSETS_26 = []
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx == 0 and dy == 0 and dz == 0:
                continue
            OFFSETS_26.append((dx, dy, dz))
OFFSETS_26 = np.array(OFFSETS_26, dtype=np.float64)  # shape (26, 3)
# Geometric length of each offset: 1 for face, sqrt(2) for edge, sqrt(3) for corner
OFFSET_LENGTHS = np.sqrt(np.sum(OFFSETS_26**2, axis=1))  # shape (26,)


class K26Lattice:
    """Minimal 3D periodic lattice with 26-neighbor connectivity and edge lengths."""

    def __init__(self, side):
        self.side = side
        self.n_nodes = side ** 3
        # Edge lengths: (n_nodes, 26), initialized to geometric length
        self.edge_lengths = np.tile(OFFSET_LENGTHS, (self.n_nodes, 1)).copy()
        # Precompute neighbor indices for all nodes
        self.neighbor_idx = np.zeros((self.n_nodes, 26), dtype=np.int64)
        for node in range(self.n_nodes):
            x, y, z = self._coords(node)
            for d in range(26):
                dx, dy, dz = int(OFFSETS_26[d, 0]), int(OFFSETS_26[d, 1]), int(OFFSETS_26[d, 2])
                nx = (x + dx) % side
                ny = (y + dy) % side
                nz = (z + dz) % side
                self.neighbor_idx[node, d] = nx * side * side + ny * side + nz

    def _coords(self, node):
        s = self.side
        x = node // (s * s)
        y = (node % (s * s)) // s
        z = node % s
        return x, y, z

    def _node(self, x, y, z):
        s = self.side
        return (x % s) * s * s + (y % s) * s + (z % s)

    def hop_distance(self, a, b):
        ax, ay, az = self._coords(a)
        bx, by, bz = self._coords(b)
        s = self.side
        dx = min(abs(ax - bx), s - abs(ax - bx))
        dy = min(abs(ay - by), s - abs(ay - by))
        dz = min(abs(az - bz), s - abs(az - bz))
        return max(dx, dy, dz)  # Chebyshev distance for k=26

    def euclidean_distance(self, a, b):
        ax, ay, az = self._coords(a)
        bx, by, bz = self._coords(b)
        s = self.side
        dx = min(abs(ax - bx), s - abs(ax - bx))
        dy = min(abs(ay - by), s - abs(ay - by))
        dz = min(abs(az - bz), s - abs(az - bz))
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def set_schwarzschild(self, center_node, r_s):
        """Set edges: e = geometric_length / (1 + r_s / max(r, 1))."""
        for node in range(self.n_nodes):
            r = self.euclidean_distance(node, center_node)
            r = max(r, 1.0)
            factor = 1.0 / (1.0 + r_s / r)
            self.edge_lengths[node, :] = OFFSET_LENGTHS * factor
        # Symmetry enforcement: edge A->B = edge B->A
        # For k=26, opposite of offset (dx,dy,dz) is (-dx,-dy,-dz)
        # Build opposite direction index
        opp = np.zeros(26, dtype=int)
        for d in range(26):
            neg = -OFFSETS_26[d]
            for d2 in range(26):
                if np.allclose(OFFSETS_26[d2], neg):
                    opp[d] = d2
                    break
        for d in range(13):  # only do half the pairs
            d2 = opp[d]
            nbs = self.neighbor_idx[:, d]
            avg = 0.5 * (self.edge_lengths[:, d] + self.edge_lengths[nbs, d2])
            self.edge_lengths[:, d] = avg
            self.edge_lengths[nbs, d2] = avg

        e_min = float(np.min(self.edge_lengths))
        e_max = float(np.max(self.edge_lengths))
        print(f"  Schwarzschild edges (r_s={r_s}): e=[{e_min:.4f}, {e_max:.4f}]")


class GeodesicBody:
    """Body that moves via geodesic frame rotation on k=26 lattice."""

    def __init__(self, node, commit_mass=5, direction=None):
        self.node = node
        self.commit_mass = commit_mass
        self.commit_counter = 0
        self.internal_direction = direction.copy() if direction is not None else np.array([0.0, 1.0, 0.0])
        self.hop_accumulator = np.zeros(3)
        self.hops = 0
        self.coord_history = []  # (tick, x, y, z)
        self.physical_position = np.zeros(3)
        self.physical_trajectory = []
        self.tilt_log = []  # (hop_num, r, |tilt|, tilt_vector)

    def advance(self, lattice, tick, star_node=None):
        """One tick: commit-count, hop, geodesic frame rotation.

        Uses full k=26 neighbors for BOTH hopping and curvature sensing.
        Hop selection: project accumulator onto all 26 offsets, pick best.
        After hop: subtract only the component that was consumed (per-axis).
        """
        self.commit_counter += 1
        if self.commit_counter < self.commit_mass:
            return False
        self.commit_counter = 0

        # Accumulate direction
        self.hop_accumulator += self.internal_direction
        abs_acc = np.abs(self.hop_accumulator)
        if np.max(abs_acc) < 0.01:
            return False

        # Axis-aligned hop (Bresenham)
        axis = int(np.argmax(abs_acc))
        sign = 1 if self.hop_accumulator[axis] >= 0 else -1
        self.hop_accumulator[axis] -= sign

        # Find face neighbor
        target_offset = np.zeros(3)
        target_offset[axis] = sign
        best_d = None
        for d in range(26):
            if np.allclose(OFFSETS_26[d], target_offset):
                best_d = d
                break

        hop_edge_length = lattice.edge_lengths[self.node, best_d]
        new_node = lattice.neighbor_idx[self.node, best_d]
        self.node = new_node
        self.hops += 1

        self.physical_position += target_offset * hop_edge_length

        # --- GEODESIC FRAME ROTATION ---
        # Per-axis: compare average 1/e for positive vs negative neighbors
        tilt = np.zeros(3)
        edges = lattice.edge_lengths[self.node]  # (26,)
        for ax in range(3):
            w_plus = 0.0
            n_plus = 0
            w_minus = 0.0
            n_minus = 0
            for d in range(26):
                component = OFFSETS_26[d, ax]
                if component > 0:
                    w_plus += 1.0 / edges[d]
                    n_plus += 1
                elif component < 0:
                    w_minus += 1.0 / edges[d]
                    n_minus += 1
            if n_plus > 0 and n_minus > 0:
                avg_plus = w_plus / n_plus
                avg_minus = w_minus / n_minus
                total = avg_plus + avg_minus
                if total > 0:
                    tilt[ax] = (avg_plus - avg_minus) / total

        # Record tilt for diagnostics
        if star_node is not None:
            r = lattice.euclidean_distance(self.node, star_node)
            self.tilt_log.append((self.hops, r, np.linalg.norm(tilt), tilt.copy()))

        tilt_mag = np.linalg.norm(tilt)
        if tilt_mag > 0:
            self.internal_direction += tilt
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        return True

    def record(self, tick, lattice):
        x, y, z = lattice._coords(self.node)
        self.coord_history.append((tick, x, y, z))


def unwrap_coords(coord_history, side):
    if len(coord_history) < 2:
        return coord_history
    result = [coord_history[0]]
    cumulative = [coord_history[0][1], coord_history[0][2], coord_history[0][3]]
    for i in range(1, len(coord_history)):
        tick = coord_history[i][0]
        for dim in range(3):
            raw = coord_history[i][dim + 1]
            prev = coord_history[i - 1][dim + 1]
            delta = raw - prev
            if delta > side // 2:
                delta -= side
            elif delta < -(side // 2):
                delta += side
            cumulative[dim] += delta
        result.append((tick, cumulative[0], cumulative[1], cumulative[2]))
    return result


def run_test(side=40, r_s=10.0, ticks=30000, commit_mass=5, separation=10):
    print("=" * 70)
    print("K=26 GEODESIC TEST: Schwarzschild edges, frame rotation")
    print("=" * 70)

    t0 = time.time()
    print(f"  Building k=26 lattice: side={side}, N={side**3}")
    lattice = K26Lattice(side)
    print(f"    Built in {time.time()-t0:.1f}s")

    # Place star at center, planet offset in +x
    cx, cy, cz = side // 2, side // 2, side // 2
    star_node = lattice._node(cx, cy, cz)
    planet_node = lattice._node(cx + separation, cy, cz)

    # Set Schwarzschild edges centered on star
    lattice.set_schwarzschild(star_node, r_s)

    # Create planet body with tangential initial direction (+y)
    planet = GeodesicBody(planet_node, commit_mass=commit_mass,
                          direction=np.array([0.0, 1.0, 0.0]))

    init_dist = lattice.euclidean_distance(star_node, planet_node)
    planet_e = float(np.mean(lattice.edge_lengths[planet_node]))
    star_e = float(np.mean(lattice.edge_lengths[star_node]))
    print(f"\n  Star at ({cx},{cy},{cz}), planet at ({cx+separation},{cy},{cz})")
    print(f"  Separation: {init_dist:.1f}")
    print(f"  r_s={r_s}, commit_mass={commit_mass}")
    print(f"  Edge at star: {star_e:.4f}, at planet: {planet_e:.4f}")

    # Run
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    distances = []
    ang_momenta = []

    t0 = time.time()
    for tick in range(ticks):
        planet.advance(lattice, tick, star_node=star_node)

        if (tick + 1) % record_interval == 0:
            planet.record(tick + 1, lattice)

        if (tick + 1) % diag_interval == 0:
            d = lattice.euclidean_distance(star_node, planet.node)
            distances.append((tick + 1, d))

            # Angular momentum (L_z = x*vy - y*vx relative to star)
            px, py, pz = lattice._coords(planet.node)
            sx, sy, sz = lattice._coords(star_node)
            s = lattice.side
            rx = px - sx
            ry = py - sy
            if rx > s // 2: rx -= s
            if rx < -(s // 2): rx += s
            if ry > s // 2: ry -= s
            if ry < -(s // 2): ry += s
            vx, vy = planet.internal_direction[0], planet.internal_direction[1]
            Lz = rx * vy - ry * vx
            ang_momenta.append((tick + 1, Lz))

            if (tick + 1) % (diag_interval * 10) == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:7d}: d={d:.1f} L={Lz:+.2f} "
                      f"dir=[{planet.internal_direction[0]:.3f},"
                      f"{planet.internal_direction[1]:.3f},"
                      f"{planet.internal_direction[2]:.3f}] ({elapsed:.1f}s)")

    final_d = lattice.euclidean_distance(star_node, planet.node)
    all_d = [d for _, d in distances]
    reversals = sum(1 for i in range(2, len(all_d))
                    if (all_d[i] - all_d[i-1]) * (all_d[i-1] - all_d[i-2]) < 0)
    print(f"\n  Distance: {init_dist:.1f} -> {final_d:.1f}")
    print(f"  Hops: {planet.hops}")
    print(f"  Range: [{min(all_d):.1f}, {max(all_d):.1f}]")
    print(f"  Reversals: {reversals}")

    # Tilt diagnostics
    if planet.tilt_log:
        rs_vals = [t[1] for t in planet.tilt_log]
        tilts = [t[2] for t in planet.tilt_log]
        print(f"\n  Tilt diagnostics:")
        # Bin by radius
        r_bins = {}
        for r, tilt_mag in zip(rs_vals, tilts):
            r_int = int(round(r))
            if r_int not in r_bins:
                r_bins[r_int] = []
            r_bins[r_int].append(tilt_mag)
        print(f"    {'r':>4s}  {'avg_tilt':>10s}  {'theory':>15s}  {'ratio':>8s}  {'n':>4s}")
        for r_int in sorted(r_bins.keys()):
            if r_int == 0:
                continue
            avg_t = np.mean(r_bins[r_int])
            theory = r_s / (2.0 * r_int * (r_int + r_s))
            ratio = avg_t / theory if theory > 0 else 0
            print(f"    {r_int:4d}  {avg_t:10.6f}  {theory:15.6f}  {ratio:8.3f}  {len(r_bins[r_int]):4d}")

    # Plot
    tag = f"k26_rs{int(r_s)}"

    # 1. Trajectory XY
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    ax = axes[0, 0]
    if planet.coord_history:
        unwrapped = unwrap_coords(planet.coord_history, lattice.side)
        xs = [c[1] for c in unwrapped]
        ys = [c[2] for c in unwrapped]
        ax.plot(xs, ys, '-', linewidth=0.5, alpha=0.7, color='blue', label='planet')
        ax.plot(xs[0], ys[0], 'go', markersize=10, label='start')
        ax.plot(xs[-1], ys[-1], 'rs', markersize=8, label='end')
    # Star position
    ax.plot(cx, cy, 'k*', markersize=15, label='star')
    ax.set_aspect('equal')
    ax.set_title(f'k=26 Trajectory (r_s={r_s})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Distance vs time
    ax = axes[0, 1]
    ax.plot([t for t, _ in distances], [d for _, d in distances], 'b-', linewidth=0.8)
    ax.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.4, label='initial')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance')
    ax.set_title(f'Distance (reversals={reversals})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Angular momentum
    ax = axes[1, 0]
    ax.plot([t for t, _ in ang_momenta], [L for _, L in ang_momenta], 'r-', linewidth=0.8)
    ax.set_xlabel('Tick')
    ax.set_ylabel('L_z')
    ax.set_title('Angular Momentum')
    ax.grid(True, alpha=0.3)

    # 4. Tilt magnitude vs radius
    ax = axes[1, 1]
    if planet.tilt_log:
        rs_log = [t[1] for t in planet.tilt_log]
        tilts_log = [t[2] for t in planet.tilt_log]
        ax.scatter(rs_log, tilts_log, s=1, alpha=0.3, c='blue')
        # Theory: r_s / (2r(r+r_s))
        r_theory = np.linspace(1, max(rs_log) + 1, 200)
        t_theory = r_s / (2 * r_theory * (r_theory + r_s))
        ax.plot(r_theory, t_theory, 'r-', linewidth=2, label=f'r_s/(2r(r+r_s))')
        ax.set_xlabel('Distance from star')
        ax.set_ylabel('|tilt|')
        ax.set_title('Tilt vs Radius')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        ax.set_xscale('log')

    fig.suptitle(f'k=26 Geodesic Test: r_s={r_s}, commit={commit_mass}, '
                 f'sep={separation}', fontsize=14, fontweight='bold')
    fig.tight_layout()
    out = RESULTS_DIR / f"phase1_trajectory_geodesic_{tag}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n  Saved: {out}")

    # Also save just the trajectory at higher resolution
    fig, ax = plt.subplots(figsize=(10, 10))
    if planet.coord_history:
        unwrapped = unwrap_coords(planet.coord_history, lattice.side)
        xs = [c[1] for c in unwrapped]
        ys = [c[2] for c in unwrapped]
        ax.plot(xs, ys, '-', linewidth=0.3, alpha=0.6, color='blue')
        ax.plot(xs[0], ys[0], 'go', markersize=12, label='start')
        ax.plot(xs[-1], ys[-1], 'rs', markersize=10, label='end')
    ax.plot(cx, cy, 'k*', markersize=20, label='star')
    ax.set_aspect('equal')
    ax.set_title(f'k=26 Orbit (r_s={r_s}, reversals={reversals})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out2 = RESULTS_DIR / f"trajectory_k26_{tag}.png"
    fig.savefig(out2, dpi=200)
    plt.close(fig)
    print(f"  Saved: {out2}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='k=26 geodesic orbit test')
    parser.add_argument('--side', type=int, default=40)
    parser.add_argument('--r-s', type=float, default=10.0)
    parser.add_argument('--ticks', type=int, default=30000)
    parser.add_argument('--commit', type=int, default=5)
    parser.add_argument('--separation', type=int, default=10)
    args = parser.parse_args()

    run_test(side=args.side, r_s=args.r_s, ticks=args.ticks,
             commit_mass=args.commit, separation=args.separation)
