import math
import json
import csv
import numpy as np
from dataclasses import dataclass, field, asdict

# ============================
# Simulation core (adapted)
# ============================

@dataclass
class SimParams:
    A_val: float = -0.1
    omega_P: float = 1.0
    delta: float = 0.1
    T: float = 100.0
    dt: float = 0.005
    c: float = 1.0
    gamma: float = 0.01
    L: float = 1.0
    Nx: int = 201
    alpha_0: float = 1.0
    alpha_1: float = 0.5
    source_pos: float = 0.5
    M: int = 2
    epsilon: float = 0.01
    x0: np.ndarray = field(default_factory=lambda: np.array([1.0, -0.5], dtype=float))

@dataclass
class SimResult:
    alpha_0: float
    gamma: float
    M: int
    total_ticks: int
    total_emissions: int
    total_agent_commits: int
    first_commit_time: float
    max_salience: float
    mean_salience: float
    cfl: float
    dt: float
    T: float

def run_sim(params: SimParams, verbose: bool = False) -> SimResult:
    # Root substrate
    A = np.array([[params.A_val, 0.0], [0.0, params.A_val]], dtype=float)
    b = np.array([0.0, 0.0], dtype=float)

    # Wave grid
    dx = params.L / (params.Nx - 1)
    xgrid = np.linspace(0.0, params.L, params.Nx)
    src_idx = int(round(params.source_pos / dx))

    # State init
    x = params.x0.copy()
    Theta = 0.0
    n_threshold = 0.0
    tick_count = 0

    # Wave field (leapfrog buffers)
    A_field = np.zeros(params.Nx, dtype=float)
    A_prev = np.zeros(params.Nx, dtype=float)

    # Agent
    Psi = 0.0
    agent_frame_count = 0
    agent_commits = 0
    first_commit_time = math.inf
    salience_sum = 0.0
    salience_max = 0.0
    salience_samples = 0

    # CFL
    cfl = params.c * params.dt / dx
    if verbose and cfl > 1.0:
        print(f"[WARN] CFL={cfl:.3f} > 1.0; reduce dt or increase Nx.")

    # Threshold initialization
    time = 0.0
    next_commit_threshold = n_threshold + 1.0 + params.delta

    # Helper inline functions
    def linear_flow_step(x, A, b, dt):
        return x + dt * (A @ x + b)

    def update_theta(Theta, omega_P, F_val, dt):
        return Theta + dt * (omega_P * F_val)

    def emit_source_amplitude(x, alpha_0, alpha_1):
        return alpha_0 + alpha_1 * np.linalg.norm(x)

    def wave_step_leapfrog(A_curr, A_prev, dt, c, gamma, src_idx, source_impulse):
        Nx = len(A_curr)
        A_next = np.empty_like(A_curr)
        for i in range(Nx):
            if i == 0:
                u_xx = (A_curr[1] - A_curr[0]) / (dx**2)
            elif i == Nx - 1:
                u_xx = (A_curr[Nx - 2] - A_curr[Nx - 1]) / (dx**2)
            else:
                u_xx = (A_curr[i + 1] - 2.0 * A_curr[i] + A_curr[i - 1]) / (dx**2)
            src = source_impulse if i == src_idx else 0.0
            u_t = (A_curr[i] - A_prev[i]) / dt
            A_next[i] = (2.0 * A_curr[i] - A_prev[i]
                         + (dt ** 2) * (c ** 2 * u_xx - gamma * u_t + src))
        return A_next

    # Main loop
    while time < params.T:
        # Root step
        x = linear_flow_step(x, A, b, params.dt)

        # Tick generator (F(x)=1)
        F_val = 1.0
        Theta = update_theta(Theta, params.omega_P, F_val, params.dt)

        emitted_source_impulse = 0.0
        if Theta >= next_commit_threshold:
            tick_count += 1
            commit_time = time

            # Emission
            q_n = emit_source_amplitude(x, params.alpha_0, params.alpha_1)
            emitted_source_impulse = q_n

            # Agent sampling on subset M
            if tick_count % params.M == 0:
                # Salience at time of commit (read current field)
                S = float(np.sum(A_field ** 2) * dx)
                salience_sum += S
                salience_max = max(salience_max, S)
                salience_samples += 1

                Psi += S  # unit refresh scaling
                if Psi >= 1.0 + params.epsilon:
                    agent_commits += 1
                    if first_commit_time == math.inf:
                        first_commit_time = commit_time
                    Psi = 0.0  # reset after commit

            # Threshold advance
            n_threshold += 1.0
            next_commit_threshold = n_threshold + 1.0 + params.delta

        # Wave step
        A_next = wave_step_leapfrog(A_field, A_prev, params.dt, params.c, params.gamma, src_idx, emitted_source_impulse)

        # Rotate buffers
        A_prev[:] = A_field[:]
        A_field[:] = A_next[:]

        time += params.dt

    mean_salience = (salience_sum / salience_samples) if salience_samples > 0 else 0.0
    first_ct = (first_commit_time if first_commit_time != math.inf else -1.0)

    return SimResult(
        alpha_0=params.alpha_0,
        gamma=params.gamma,
        M=params.M,
        total_ticks=tick_count,
        total_emissions=tick_count,  # one emission per tick
        total_agent_commits=agent_commits,
        first_commit_time=first_ct,
        max_salience=salience_max,
        mean_salience=mean_salience,
        cfl=cfl,
        dt=params.dt,
        T=params.T
    )

# ============================
# Sweep runner
# ============================

def run_sweep(alpha0_list, gamma_list, M_list,
              base: SimParams,
              out_csv="threshold_surface_results.csv",
              out_json="threshold_surface_results.json",
              verbose=False):

    results = []
    for alpha_0 in alpha0_list:
        for gamma in gamma_list:
            for M in M_list:
                p = SimParams(**asdict(base))
                p.alpha_0 = alpha_0
                p.gamma = gamma
                p.M = M
                res = run_sim(p, verbose=verbose)
                results.append(res)
                if verbose:
                    status = "COMMITS" if res.total_agent_commits > 0 else "NO COMMITS"
                    print(f"[RUN] α0={alpha_0:.3f} γ={gamma:.4f} M={M} -> "
                          f"{status}, commits={res.total_agent_commits}, firstCt={res.first_commit_time:.2f}, "
                          f"maxS={res.max_salience:.6f}, meanS={res.mean_salience:.6f}, CFL={res.cfl:.3f}")

    # Save CSV
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "alpha_0", "gamma", "M", "total_ticks", "total_emissions",
            "total_agent_commits", "first_commit_time", "max_salience",
            "mean_salience", "cfl", "dt", "T"
        ])
        for r in results:
            writer.writerow([
                r.alpha_0, r.gamma, r.M, r.total_ticks, r.total_emissions,
                r.total_agent_commits, r.first_commit_time, r.max_salience,
                r.mean_salience, r.cfl, r.dt, r.T
            ])

    # Save JSON
    with open(out_json, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    return results

# ============================
# Entry point
# ============================
if __name__ == "__main__":
    base = SimParams(
        # Keep fixed values aligned with your recent runs
        A_val=-0.1, omega_P=1.0, delta=0.1,
        T=100.0, dt=0.005,
        c=1.0, gamma=0.01,  # gamma will be swept
        L=1.0, Nx=201,
        alpha_0=1.0, alpha_1=0.5,  # alpha_0 will be swept
        source_pos=0.5,
        M=2,  # M will be swept
        epsilon=0.01,
        x0=np.array([1.0, -0.5], dtype=float)
    )

    alpha0_list = [1.6, 1.7, 1.8, 1.85, 1.90, 2.0, 3.0, 5.0]
    gamma_list = [0.01, 0.005, 0.001, 0.0005]
    M_list = [1, 2, 4]

    results = run_sweep(
        alpha0_list, gamma_list, M_list,
        base=base,
        out_csv="threshold_surface_results.csv",
        out_json="threshold_surface_results.json",
        verbose=True
    )

    # Quick summary counts per parameter slice (optional)
    # e.g., how many runs with commits for each gamma
    by_gamma = {}
    for r in results:
        by_gamma.setdefault(r.gamma, 0)
        by_gamma[r.gamma] += (1 if r.total_agent_commits > 0 else 0)
    print("\nCommit counts by gamma:")
    for g, count in sorted(by_gamma.items()):
        print(f"  gamma={g:.4f}: {count} committing runs")