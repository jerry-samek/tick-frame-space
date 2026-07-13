"""Does the framework escape the LeSage HEATING problem? (RAW 135 §13.4 open)

Classical LeSage heats catastrophically: to get gravity's strength the flux
must be intense, and absorbing it cooks the body. The reason is a GOD-VIEW
assumption -- gravity = absorbing energetic corpuscles (E = p*c, momentum and
energy LOCKED), so a big momentum-shadow (gravity) forces a big energy-deposit
(heat).

Inside-out, gravity is NOT absorption of energetic corpuscles. It is a SHADOW
IN THE RENEWAL RATE: the mass slows how often the local vacuum tick-stream
renews (a timing/lag effect -- Exp 128 v11 "renewal is the local ambient
tick-stream"). A rate-shadow carries momentum/pressure (-> gravity) but ~no
energy. So the energy-per-shadow ratio eta decouples: classical eta ~ 1
(locked); framework eta << 1 (the consumed renewal is depleted/low-energy,
RAW 135 §4). Gravity ~ shadow ~ s; heat-in ~ eta * s. Plus RENEWAL prevents an
internal reservoir from accumulating (same axiom that defeated drag).

Test: equilibrium internal energy (temperature) vs gravity strength (s), for
classical (eta=1, persistent) vs framework (eta<<1, renewing). Show the
framework can have STRONG gravity and LOW temperature; classical cannot.
"""

import numpy as np


def equilibrium_temperature(s, eta, sigma=0.05, W=1, flux=1.0, ticks=4000):
    """Internal energy E: gains eta*s*flux/tick (energy locked to the shadow by
    eta), radiates sigma*E/tick; renewal every W ticks re-renders the pattern,
    resetting stored energy toward the freshly-consumed baseline (no reservoir
    carries across a renewal). Return steady-state E."""
    E = 0.0
    base = eta * s * flux           # energy delivered per tick by the shadow flux
    for t in range(1, ticks + 1):
        E += base                    # consume (energy in, scaled by eta)
        E -= sigma * E               # radiate (shed)
        if t % W == 0:
            # renewal: the new instance is built from the current (depleted)
            # flux, not the accumulated reservoir -> stored heat above the
            # single-cycle intake does not persist.
            E = min(E, base * W)
    return E


def main():
    print("Gravity strength ~ s (the renewal-rate shadow). Heat-in ~ eta*s "
          "(eta = energy per unit shadow).")
    print("Classical LeSage: eta=1 (energy locked to momentum), persistent "
          "(W large). Framework: eta<<1 (depleted rate-shadow) + renewal (W=1).\n")
    print(f"{'gravity s':>10}{'classical T (eta=1,persist)':>30}"
          f"{'framework T (eta=.02,W=1)':>28}")
    for s in (0.1, 0.3, 0.5, 1.0, 2.0):
        Tc = equilibrium_temperature(s, eta=1.0, W=100000)
        Tf = equilibrium_temperature(s, eta=0.02, W=1)
        print(f"{s:>10.1f}{Tc:>30.2f}{Tf:>28.3f}")

    print("\n=== decoupling check: sweep gravity at fixed eta -- does heat track "
          "gravity or the eta-scaled shadow? ===")
    print(f"{'s (gravity)':>12}{'heat-in rate (eta=.02)':>24}{'ratio heat/gravity':>20}")
    for s in (0.2, 0.5, 1.0, 2.0):
        heat = 0.02 * s
        print(f"{s:>12.1f}{heat:>24.4f}{heat/s:>20.4f}")

    print("\n=== renewal vs persistence at classical energy (eta=1): does "
          "renewal alone cap the reservoir? ===")
    print(f"{'W':>8}{'equilibrium T (eta=1, s=1)':>28}")
    for W in (1, 5, 20, 100, 100000):
        T = equilibrium_temperature(1.0, eta=1.0, W=W)
        tag = "(persistent)" if W == 100000 else ""
        print(f"{W:>8}{T:>28.2f}  {tag}")

    print("\nReading: gravity's strength is set by the shadow s; heat by eta*s. "
          "Classical locks eta=1 -> big gravity forces big heat. The framework's "
          "gravity is a renewal-RATE shadow (eta<<1, energy-free timing effect), "
          "so strong gravity carries little heat -- the momentum/energy lock is a "
          "god-view artifact. Renewal additionally caps any reservoir. Both the "
          "sign, the drag, and the heating dissolve the same way: gravity is "
          "inside-out timing, not god-view energetic absorption. Prediction: a "
          "gravitating body still radiates its OWN metabolism (luminosity), just "
          "not from gravitational absorption.")


if __name__ == "__main__":
    main()
