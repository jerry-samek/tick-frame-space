"""Exp 137 Phase 1 — T6 decisive follow-ups (skeptic-mandated).

Addresses the skeptic's three load-bearing challenges:
  (E) fixed-K / different-embedding: a genuinely 3D K=8 survivor (Hamiltonian
      cycle on a unit cube) vs the coplanar F3_K8. If rank is identical across
      embeddings at fixed K, the reading tracks period/size, not 3D embedding.
  (C) confinement under off-ring & large perturbations with a wide 3D window:
      does damage EVER leave the ring / the z=0 plane?
  (S) proper T6.2a statistics: 100 shuffle surrogates, pooled sd, evaluate the
      REGISTERED "2 pooled sd" criterion instead of the ad-hoc >1.0.
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from substrate import face_neighbors
from rule import bootstrap
from multipattern import tick_multi
from fixtures import F3_K8_RING
from readout import dpr_sub
from phase1_t6 import observables, limit_cycle_phases
from phase0b_deconfound import mds_dim90c  # noqa: F401

# A genuinely 3D K=8 survivor: Hamiltonian cycle on the unit cube.
CUBE_K8 = [
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
    (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1),
]


def sustains(cycle, ticks=48):
    """Does the rule hold this cycle as a period-K fixed point (no wedge/non-unique)?"""
    cv = {}
    bootstrap(cv, cycle, 1)
    hashes = []
    try:
        for _ in range(ticks):
            hashes.append(tuple(sorted(cv.items())))
            tick_multi(cv)
    except Exception as e:  # noqa: BLE001
        return False, f"exception: {e}"
    K = len(cycle)
    # period-K check on the tail
    per_ok = all(hashes[i] == hashes[i + K] for i in range(len(hashes) - K - 1))
    alive = len([c for c in cv if cv[c] != 0])
    return (per_ok and alive == K), f"period_K={per_ok} alive={alive}/{K}"


def box_window(cycle, pad=3, zpad=2):
    xs = [c[0] for c in cycle]; ys = [c[1] for c in cycle]; zs = [c[2] for c in cycle]
    cells = []
    for x in range(min(xs) - pad, max(xs) + pad + 1):
        for y in range(min(ys) - pad, max(ys) + pad + 1):
            for z in range(min(zs) - zpad, max(zs) + zpad + 1):
                cells.append((x, y, z))
    return cells


def r2_generic(cycle, perturb, W_factor=20, window=None):
    """R2 divergence field with a pluggable perturbation function.
    perturb(per_dict, phase_state) mutates per in place to inject damage."""
    K = len(cycle)
    W = W_factor * K
    window = window or box_window(cycle)
    phases = limit_cycle_phases(cycle, 1)
    samples = []
    off_plane_hits = 0
    off_ring_hits = 0
    ring = set(cycle)
    plane_z = set(c[2] for c in cycle)
    for phi in range(K):
        base = phases[phi]
        for pert in perturb(cycle, base):
            ref = dict(base); per = dict(pert)
            for _ in range(W):
                tick_multi(ref); tick_multi(per)
                d = {c: per.get(c, 0) - ref.get(c, 0) for c in window}
                samples.append([d[c] for c in window])
                for c, val in d.items():
                    if val != 0:
                        if c not in ring:
                            off_ring_hits += 1
                        if c[2] not in plane_z:
                            off_plane_hits += 1
    return np.array(samples, float), off_ring_hits, off_plane_hits


def perturb_onring(cycle, base, mag=1):
    out = []
    for s in cycle:
        for sgn in (+1, -1):
            per = dict(base); per[s] = per.get(s, 0) + sgn * mag
            if per[s] == 0:
                del per[s]
            out.append(per)
    return out


def perturb_offring(cycle, base):
    """Inject a +K deposit onto a face-neighbor collar cell (off-ring)."""
    ring = set(cycle); out = []
    seen = set()
    for s in cycle:
        for nb in face_neighbors(s):
            if nb not in ring and nb not in seen:
                seen.add(nb)
                per = dict(base); per[nb] = len(cycle)  # strong off-ring deposit
                out.append(per)
    return out


def perturb_delete(cycle, base):
    out = []
    for s in cycle:
        per = dict(base)
        per.pop(s, None)  # delete a ring cell outright
        out.append(per)
    return out


def main():
    print("=== (E) fixed-K different-embedding: does a 3D K=8 survivor exist? ===")
    ok, msg = sustains(CUBE_K8)
    print(f"CUBE_K8 sustains: {ok}  ({msg})")
    flat_ok, flat_msg = sustains(F3_K8_RING)
    print(f"FLAT_K8 sustains: {flat_ok}  ({flat_msg})")

    if ok:
        sc, orc, oph = r2_generic(CUBE_K8, perturb_onring)
        sf, orf, ophf = r2_generic(F3_K8_RING, perturb_onring)
        oc = observables(sc); of = observables(sf)
        print(f"\nR2 dpr_sub  CUBE_K8={oc['dpr_sub']:.3f} (n_active={oc['n_active']}, "
              f"off_ring_hits={orc}, off_plane_hits={oph})")
        print(f"R2 dpr_sub  FLAT_K8={of['dpr_sub']:.3f} (n_active={of['n_active']}, "
              f"off_ring_hits={orf}, off_plane_hits={ophf})")
        print(f"  => embedding changes rank? "
              f"{'YES (instrument reads embedding -> FAIL refuted)' if abs(oc['dpr_sub']-of['dpr_sub'])>0.5 else 'NO (rank tracks period/size, not embedding)'}")
    else:
        print("  CUBE_K8 does not sustain; a 3D survivor at K=8 may not exist under the rule.")

    print("\n=== (C) confinement under off-ring & delete perturbations, wide 3D window ===")
    for label, pf in (("onring_mag1", lambda c, b: perturb_onring(c, b, 1)),
                      ("onring_magK", lambda c, b: perturb_onring(c, b, len(c))),
                      ("offring_+K", perturb_offring),
                      ("delete_cell", perturb_delete)):
        s, orh, oph = r2_generic(F3_K8_RING, pf, W_factor=20)
        o = observables(s)
        print(f"FLAT_K8 {label:<14}: dpr_sub={o['dpr_sub']:.3f} n_active={o['n_active']} "
              f"off_ring_hits={orh} off_plane_hits={oph} frac_nz={o['frac_nonzero']:.3f}")

    print("\n=== (S) proper T6.2a statistics: 100 shuffle surrogates, 2-pooled-sd ===")
    from phase1_t6 import r2_damage, shuffle_null, FIXTURES
    rng = np.random.default_rng(0)
    for name, cyc in FIXTURES.items():
        s = r2_damage(cyc)
        real = observables(s)["dpr_sub"]
        sh = [observables(shuffle_null(s, rng))["dpr_sub"] for _ in range(100)]
        m, sd = float(np.mean(sh)), float(np.std(sh))
        pooled = sd  # real is a single deterministic point; surrogate sd is the scale
        z = abs(real - m) / pooled if pooled > 0 else float("inf")
        print(f"{name}: real={real:.3f} surrogate={m:.3f}+/-{sd:.3f} "
              f"|diff|/sd={z:.2f} passes_2sd={z >= 2.0}")


if __name__ == "__main__":
    main()
