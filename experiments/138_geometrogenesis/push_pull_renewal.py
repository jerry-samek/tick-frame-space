"""Kill-switch test (RAW 135 §12.1): does the attractive consumption-PULL beat
the repulsive radiation-PUSH, or is it LeSage's grave?

The honest mechanism (correcting RAW 135 §6, whose "push averages to jitter" is
dubious -- steady radiation pressure is a steady force, it accumulates):

  - PUSH = momentum. Absorbed outward-moving flux adds outward VELOCITY.
    v += alpha * Phi(r) each tick. Accumulates.
  - PULL = accretion (RAW 135 §4: the body grows toward the source). A direct
    inward POSITION shift, capped by consumption capacity C:
    r -= beta * min(Phi(r), C) each tick. Persists.
  - RENEWAL (Doc 28): every W ticks the pattern is renewed -- a NEW bundle --
    so its accumulated VELOCITY resets to 0. Its accreted POSITION carries over.

Renewal thus resets the push channel but not the pull channel. Prediction: a
fast-renewing pattern (small W) keeps the push bounded (~alpha*Phi*W^2/2 per
cycle) below the accretion drift (~beta*Phi*W per cycle), so PULL wins = gravity;
a slow/never-renewing pattern (large W) lets the push run away = LeSage. Critical
period W* ~ 2*beta/alpha. We sweep W and beta/alpha and locate the transition.

Phi(r) = 1/r^2 (3D flux dilution, = the 1/N(r) of the flooding-lag substrate).
"""

import numpy as np


def trajectory(r0=20.0, alpha=0.02, beta=0.02, cap=1.0, W=10, ticks=6000,
               dt=1.0, pull_mode="accretion"):
    """Radial test pattern under push (velocity) + pull + renewal.
    pull_mode: 'accretion' (RAW 135 §4 -- pull shifts POSITION, persists) or
    'force' (Exp 128 v11 -- pull changes VELOCITY, same kind as push).
    Returns outcome ('infall' | 'escape' | 'bound') and final/min radius."""
    r, v = r0, 0.0
    rmin = r0
    for t in range(1, ticks + 1):
        phi = 1.0 / (r * r)
        v += alpha * phi                       # push: outward momentum
        if pull_mode == "force":
            v -= beta * min(phi, cap)           # pull as force: inward velocity
        r += v * dt
        if pull_mode == "accretion":
            r -= beta * min(phi, cap) * dt       # pull as accretion: inward position
        if t % W == 0:
            v = 0.0                             # renewal: velocity resets
        rmin = min(rmin, r)
        if r <= 1.0:
            return "infall", r, rmin
        if r > 4 * r0:
            return "escape", r, rmin
    outcome = "bound" if abs(r - r0) < 0.1 * r0 else \
        ("infall" if r < r0 else "escape")
    return outcome, r, rmin


def main():
    print("=== kill switch: renewal period W vs outcome (alpha=beta=0.02, "
          "predicted W* ~ 2*beta/alpha = 2) ===")
    print(f"{'W':>4}  {'outcome':<10}{'final_r':>9}{'min_r':>8}")
    for W in (1, 2, 3, 5, 10, 20, 50, 100, 100000):
        oc, rf, rmin = trajectory(W=W)
        tag = "(no renewal)" if W == 100000 else ""
        print(f"{W:>4}  {oc:<10}{rf:>9.2f}{rmin:>8.2f}  {tag}")

    print("\n=== is the transition governed by W* ~ 2*beta/alpha? sweep the "
          "coupling ratio at fixed W=5 ===")
    print(f"{'beta/alpha':>11}  {'outcome':<10}{'min_r':>8}   (infall expected when 2*beta/alpha > W=5)")
    alpha = 0.02
    for ratio in (0.5, 1.0, 2.0, 3.0, 5.0, 8.0):
        oc, rf, rmin = trajectory(alpha=alpha, beta=alpha * ratio, W=5)
        print(f"{ratio:>11.1f}  {oc:<10}{rmin:>8.2f}   (2*ratio={2*ratio:.0f})")

    print("\n=== the modeling FORK: does the pull act as accretion (position) "
          "or force (velocity)? (W=10) ===")
    print(f"{'beta/alpha':>11}  {'accretion':<12}{'force':<12}")
    for ratio in (0.5, 1.0, 1.5, 2.0, 4.0):
        oa, _, ra = trajectory(beta=0.02 * ratio, W=10, pull_mode="accretion")
        of, _, rf = trajectory(beta=0.02 * ratio, W=10, pull_mode="force")
        print(f"{ratio:>11.1f}  {oa+f'({ra:.0f})':<12}{of+f'({rf:.0f})':<12}")

    print("\nReading (honest): the kill switch's resolution HINGES ON THE PULL "
          "MECHANISM, and the framework's two candidates disagree.\n"
          "  - pull=ACCRETION (RAW 135 §4): the steady push generically wins "
          "(escape) except in the degenerate W=1 / very-high-beta limit -> "
          "LeSage risk stands.\n"
          "  - pull=FORCE (Exp 128 v11, the EARNED 1/r^2+Kepler result): net "
          "force ~ (beta-alpha)/r^2, so infall iff beta>alpha (the Eddington "
          "condition), renewal irrelevant to the sign.\n"
          "So gravity survives IFF the pull is a force and beta>alpha. Whether "
          "consumption pulls as force or accretion is UNRESOLVED -- and RAW 135 "
          "§6's 'push averages to jitter' is refuted (a steady force accumulates).")


if __name__ == "__main__":
    main()
