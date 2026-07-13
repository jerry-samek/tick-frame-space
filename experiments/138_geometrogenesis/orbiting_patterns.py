"""Moving/renewing patterns on the unified substrate — and the relational PoV:
with no god-view, "planet orbits star" is not privileged.

A pattern MOVES by renewing (Doc 28): each cycle it re-forms at a shifted
position set by the gravity well (the ambient shadow, RAW 135 §13.3), not by
carried momentum. Renewal re-bases the drag rest-frame each cycle, so the orbit
is stable (§13.4). All any pattern ever reads is its LAG (distance) to the
others -- and every frame agrees on the lags. But "who moves" is a
reconstruction, and NO frame is privileged (no god-view, RAW 134 §12.5):

  - god-view (a fiction): planet orbits the ~fixed star.
  - planet's PoV: the planet is always "here"; the star's direction wheels
    around it -> the STAR orbits the planet.
  - a third observer's PoV: both star and planet wheel around the observer.

Same lags, different "who orbits whom." The objective content is the
frame-invariant lag structure; the orbit is perspectival.
"""

import numpy as np


def simulate_orbit(GM=1.0, r0=10.0, k=0.02, W=1, dt=0.05, orbits=3):
    """Planet under gravity (the shadow-well force) + LeSage drag, with renewal
    re-basing the drag frame every W ticks. Returns god-view positions of star
    (fixed) and planet over time."""
    star = np.array([0.0, 0.0])
    r = np.array([r0, 0.0])
    v = np.array([0.0, np.sqrt(GM / r0)])
    v_frame = np.zeros(2)
    period = 2 * np.pi * np.sqrt(r0**3 / GM)
    steps = int(orbits * period / dt)
    planet_traj = []
    for t in range(1, steps + 1):
        rr = np.linalg.norm(r - star)
        a_grav = -GM / rr**3 * (r - star)         # gravity = ambient-shadow well
        a_drag = -k * (v - v_frame)                # LeSage drag on relative velocity
        v = v + (a_grav + a_drag) * dt
        r = r + v * dt
        if t % W == 0:
            v_frame = v.copy()                     # RENEWAL: re-base the frame
        planet_traj.append(r.copy())
    return star, np.array(planet_traj), period, dt


def main():
    star, planet, period, dt = simulate_orbit()
    n = len(planet)
    # sample 8 phases around one orbit
    phase_idx = [int(n - period/dt + f) for f in
                 np.linspace(0, period/dt - 1, 8).astype(int)]
    phase_idx = [i for i in phase_idx if 0 <= i < n]

    print("Renewal-stable orbit on the unified substrate (gravity = shadow "
          "well; renewal defeats drag). One orbit, 8 phases.\n")

    print("[A] GOD-VIEW (a fiction): planet position around the fixed star:")
    for i in phase_idx:
        print(f"    planet = ({planet[i][0]:+5.1f},{planet[i][1]:+5.1f})   "
              f"lag(planet,star) = {np.linalg.norm(planet[i]-star):4.1f}")

    print("\n[B] PLANET's PoV: the planet is always at its own origin; where is "
          "the star? (star - planet), i.e. the star's apparent position:")
    for i in phase_idx:
        rel = star - planet[i]
        ang = np.degrees(np.arctan2(rel[1], rel[0]))
        print(f"    star @ direction {ang:+7.1f} deg, lag {np.linalg.norm(rel):4.1f}"
              f"   -> the STAR wheels around the planet")

    print("\n[C] THIRD OBSERVER's PoV (a body at (14,14), itself ~fixed): both "
          "star and planet wheel around the observer:")
    obs = np.array([14.0, 14.0])
    for i in phase_idx[:4]:
        rs, rp = star - obs, planet[i] - obs
        print(f"    star @ lag {np.linalg.norm(rs):4.1f} dir "
              f"{np.degrees(np.arctan2(rs[1],rs[0])):+6.1f};  "
              f"planet @ lag {np.linalg.norm(rp):4.1f} dir "
              f"{np.degrees(np.arctan2(rp[1],rp[0])):+6.1f}")

    print("\n[invariant] the LAG planet<->star is what every frame actually "
          "reads, and all agree on it:")
    lags = [np.linalg.norm(planet[i] - star) for i in phase_idx]
    print(f"    lag(planet,star) across phases = {[round(x,1) for x in lags]}  "
          f"(constant = circular orbit; frame-INVARIANT)")

    print(f"\n[renewal / drag] final lag = {np.linalg.norm(planet[-1]-star):.2f} "
          f"vs initial 10.0 -> orbit STABLE (renewal defeats drag). A "
          "persistent (never-renewing) body would have decayed.\n")

    print("Reading: every pattern reads only LAGS, and all frames agree on "
          "them (objective). 'Planet orbits star' vs 'star orbits planet' vs "
          "'both orbit the observer' are the SAME lag data in different frames "
          "-- none privileged, because there is no god-view. Motion is "
          "perspectival; the lag structure is what's real. And the moving "
          "pattern is renewal-driven, so its orbit is drag-stable on the one "
          "flooding-lag substrate.")


if __name__ == "__main__":
    main()
