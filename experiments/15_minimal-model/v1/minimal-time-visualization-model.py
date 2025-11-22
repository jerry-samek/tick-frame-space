"""
Minimal time–visualization model:
- Root substrate: 2D linear ODE
- Tick generator: Planck-scaled accumulator with F(x)=1
- PoF commits: threshold crossings at n + delta
- Artefact field: 1D damped wave equation driven by tick emissions
- Agent refresh: subset of ticks with salience detection
- Logs: tick commits, artefact emissions, agent percepts
"""

import math
import numpy as np

# -----------------------------
# Parameters
# -----------------------------
A = np.array([[-0.1, 0.0],
              [ 0.0, -0.1]], dtype=float)
b = np.array([0.0, 0.0], dtype=float)

omega_P = 1.0     # Planck-scaled frequency (unit baseline)
delta = 0.1       # hysteresis margin for PoF commit
T = 10.0          # simulation horizon
dt = 0.005        # timestep (reduced for CFL stability)
N_steps = int(T / dt)

# Wave field parameters (1D lattice)
c = 1.0           # wave speed
gamma = 0.01      # damping
L = 1.0           # spatial domain length
Nx = 201          # grid points
dx = L / (Nx - 1)
xgrid = np.linspace(0.0, L, Nx)

alpha_0 = 1.0     # base emission amplitude
alpha_1 = 0.5     # amplitude scales with ||x||
source_pos = 0.5  # emission position (middle of domain)

# Agent parameters
M = 2             # downsampling factor (agent reads every M-th tick)
epsilon = 0.01    # agent commit hysteresis margin

# -----------------------------
# State initialization
# -----------------------------
x = np.array([1.0, -0.5], dtype=float) # initial root state
Theta = 0.0                             # progress accumulator
n_threshold = 0.0                       # current threshold base (integer part)
tick_count = 0                          # total PoF commits

# Wave field: use leapfrog scheme variables
A_field = np.zeros(Nx, dtype=float)     # field at current time
A_prev = np.zeros(Nx, dtype=float)      # field at previous time
A_next = np.zeros(Nx, dtype=float)      # field at next time
# Initialize A_prev for leapfrog (assume small)
A_prev[:] = A_field[:]

# Index of source position on grid
src_idx = int(round(source_pos / dx))

# Logs
tick_log = []
emission_log = []
agent_log = []

# Agent accumulators
Psi = 0.0
agent_frame_count = 0
last_agent_commit_time = -math.inf

# Stability checks for wave CFL
cfl = c * dt / dx
if cfl > 1.0:
    print(f"[WARN] CFL condition violated (c*dt/dx={cfl:.3f} > 1). Reduce dt or increase Nx.")

# -----------------------------
# Helper functions
# -----------------------------
def linear_flow_step(x, A, b, dt):
    # Explicit Euler for simplicity (stable A keeps it reasonable)
    return x + dt * (A @ x + b)

def update_theta(Theta, omega_P, F_val, dt):
    return Theta + dt * (omega_P * F_val)

def emit_source_amplitude(x, alpha_0, alpha_1):
    return alpha_0 + alpha_1 * np.linalg.norm(x)

def wave_step_leapfrog(A_curr, A_prev, dt, c, gamma, src_idx, source_impulse):
    """
    Damped 1D wave: u_tt - c^2 u_xx + gamma u_t = source
    Leapfrog discretization with simple damping and explicit source.
    """
    Nx = len(A_curr)
    A_next = np.empty_like(A_curr)

    # second spatial derivative (Neumann BCs: zero gradient at boundaries)
    # d2u/dx2 approximated with central differences
    # Boundary: reflect or zero-gradient
    for i in range(Nx):
        if i == 0:
            u_xx = (A_curr[1] - A_curr[0]) / (dx**2)  # forward diff approx
        elif i == Nx - 1:
            u_xx = (A_curr[Nx - 2] - A_curr[Nx - 1]) / (dx**2)  # backward diff approx
        else:
            u_xx = (A_curr[i + 1] - 2.0 * A_curr[i] + A_curr[i - 1]) / (dx**2)

        # source term (impulse at src_idx)
        src = source_impulse if i == src_idx else 0.0

        # Leapfrog: u_next = 2u - u_prev + dt^2*(c^2 u_xx - gamma u_t + src)
        # approximate u_t with (u - u_prev)/dt
        u_t = (A_curr[i] - A_prev[i]) / dt
        A_next[i] = (2.0 * A_curr[i] - A_prev[i]
                     + (dt ** 2) * (c ** 2 * u_xx - gamma * u_t + src))

    return A_next

def agent_salience(A_field):
    # Simple energy detector over the entire domain
    return float(np.sum(A_field ** 2) * dx)

# -----------------------------
# Main simulation loop
# -----------------------------
time = 0.0
next_commit_threshold = n_threshold + 1.0 + delta  # first threshold at 1+delta

# Agent reads every M-th tick; manage via tick_count modulo M
while time < T:
    # 1) Root substrate step
    x = linear_flow_step(x, A, b, dt)

    # 2) Tick generator (F(x)=1)
    F_val = 1.0
    Theta = update_theta(Theta, omega_P, F_val, dt)

    # 3) PoF commit check: crossing n + delta (integer + hysteresis margin)
    emitted_source_impulse = 0.0
    if Theta >= next_commit_threshold:
        tick_count += 1
        commit_time = time
        # Log PoF commit
        tick_log.append({
            "TickID": tick_count,
            "time": commit_time,
            "Theta": Theta,
            "x": x.copy(),
            "F": F_val,
            "Mode": "COMMIT",
        })
        print(f"[TICK] n={tick_count:04d} t={commit_time:.3f} Theta={Theta:.3f} x={x}")

        # 4) Emission: impulse strength depends on ||x||
        q_n = emit_source_amplitude(x, alpha_0, alpha_1)
        emitted_source_impulse = q_n
        emission_log.append({
            "TickID": tick_count,
            "time": commit_time,
            "pos": source_pos,
            "strength": q_n
        })
        print(f"  [EMIT] at x={source_pos:.2f} strength={q_n:.3f}")

        # 5) Advance threshold to next integer + delta
        n_threshold += 1.0
        next_commit_threshold = n_threshold + 1.0 + delta

        # 6) Agent subset rule: only process percept on every M-th tick
        if tick_count % M == 0:
            # Compute salience and update agent accumulator
            S = agent_salience(A_field)
            Psi += S * 1.0  # scale by unit refresh rate baseline
            if Psi >= 1.0 + epsilon:
                agent_frame_count += 1
                agent_log.append({
                    "FrameID": agent_frame_count,
                    "time": commit_time,
                    "Psi": Psi,
                    "Salience": S,
                    "Mode": "COMMIT"
                })
                print(f"    [AGENT COMMIT] k={agent_frame_count:04d} t={commit_time:.3f} Psi={Psi:.3f} S={S:.6f}")
                Psi = 0.0
            else:
                # No commit; log a repeat
                agent_log.append({
                    "FrameID": agent_frame_count,
                    "time": commit_time,
                    "Psi": Psi,
                    "Salience": S,
                    "Mode": "REPEAT"
                })
                print(f"    [AGENT] no commit: Psi={Psi:.3f} S={S:.6f}")

    # 7) Wave field step with possible source impulse
    A_next = wave_step_leapfrog(A_field, A_prev, dt, c, gamma, src_idx, emitted_source_impulse)

    # Rotate wave buffers
    A_prev[:] = A_field[:]
    A_field[:] = A_next[:]

    # Advance time
    time += dt

# -----------------------------
# Summary
# -----------------------------
print("\n--- Summary ---")
print(f"Total ticks: {tick_count}")
print(f"Total agent frames: {len(agent_log)}")
print(f"Total emissions: {len(emission_log)}")