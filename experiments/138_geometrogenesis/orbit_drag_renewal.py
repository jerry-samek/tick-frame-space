"""Does RENEWAL defeat LeSage drag? (RAW 135 §13.3 open frontier)

LeSage/shadow gravity is attractive (kill switch settled) but classically
suffers DRAG: a body moving through the flux bath sees aberrated (forward-
tilted) flux, which saps its momentum and decays orbits. Aberration -- hence
drag -- is proportional to the body's velocity RELATIVE TO THE BATH at the
moment it reads the flux.

Tom's resolution: in this framework entities do not persist-and-move; they
RENEW (Doc 28). Each renewed instance forms fresh from its local bath, so at
the moment it reads it is AT REST in its own renewed frame. Drag can only act
on the velocity acquired SINCE the last renewal (~ acceleration * W), never on
the full orbital velocity, which is baked into the renewed rest-frame. So a
fast-renewing body feels ~no drag; a persistent (never-renewing) body feels the
full LeSage drag and decays.

Test: a 2D orbit under central gravity GM/r^2, plus drag F = -k * v_rel, where
v_rel = v - v_frame and v_frame is re-set to the body's current velocity every
W ticks (renewal). Sweep W. Prediction: large W (persistent) -> orbit decays;
small W (renewing) -> orbit stable. Non-question-begging: the renewal never
touches POSITION or the orbital velocity directly -- it only re-bases the frame
that drag is measured against.
"""

import numpy as np


def run_orbit(GM=1.0, r0=10.0, k=0.02, W=1, dt=0.05, orbits=25):
    """Return (r_initial, r_final, min_r, decayed?) for renewal period W."""
    r = np.array([r0, 0.0])
    v = np.array([0.0, np.sqrt(GM / r0)])      # circular orbit
    v_frame = np.zeros(2)                        # bath frame = static (classical
    #   LeSage). Renewal re-bases it to the body's current v every W ticks; if
    #   it never renews, it stays 0 = full classical drag on the orbital speed.
    period = 2 * np.pi * np.sqrt(r0**3 / GM)
    steps = int(orbits * period / dt)
    rmin = r0
    for t in range(1, steps + 1):
        rr = np.linalg.norm(r)
        if rr < 0.5:
            return r0, rr, min(rmin, rr), True    # crashed in
        a_grav = -GM / rr**3 * r                  # central gravity
        v_rel = v - v_frame                        # velocity since last renewal
        a_drag = -k * v_rel                         # LeSage drag on relative velocity
        v = v + (a_grav + a_drag) * dt
        r = r + v * dt
        if t % W == 0:
            v_frame = v.copy()                     # RENEWAL: re-base the rest-frame
        rmin = min(rmin, np.linalg.norm(r))
    rf = np.linalg.norm(r)
    return r0, rf, rmin, (rf < 0.7 * r0)


def main():
    print("Orbit under gravity + LeSage drag (k=0.02). Renewal re-bases the "
          "drag rest-frame every W ticks.")
    print("Prediction: large W (persistent body) -> decay; small W (renewing) "
          "-> stable.\n")
    print(f"{'W':>8}  {'r_final/r0':>11}{'min_r/r0':>10}   outcome")
    for W in (1, 2, 5, 10, 50, 200, 100000):
        r0, rf, rmin, decayed = run_orbit(W=W)
        tag = "(never renews)" if W == 100000 else ""
        oc = "DECAYED" if decayed else ("crashed" if rmin < 1 else "stable")
        print(f"{W:>8}  {rf/r0:>11.3f}{rmin/r0:>10.3f}   {oc}  {tag}")

    print("\n=== drag strength sweep at fast renewal (W=1) vs no renewal ===")
    print(f"{'k':>8}  {'W=1 r_f/r0':>12}{'no-renew r_f/r0':>17}")
    for k in (0.01, 0.05, 0.1, 0.2):
        _, rf1, _, _ = run_orbit(k=k, W=1)
        _, rfn, _, _ = run_orbit(k=k, W=100000)
        print(f"{k:>8}  {rf1/10:>12.3f}{rfn/10:>17.3f}")

    print("\nReading: if fast renewal keeps the orbit stable while a persistent "
          "body decays at the same drag k, then RENEWAL DEFEATS LeSage DRAG -- "
          "because the entity does not move through the bath; it renews at rest "
          "in its local frame, and only its tiny since-renewal velocity is "
          "draggable. Motion is a rendering-shift, not a plow through a medium.")


if __name__ == "__main__":
    main()
