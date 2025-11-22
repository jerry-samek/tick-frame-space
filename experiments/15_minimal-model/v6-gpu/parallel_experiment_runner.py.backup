"""
Parallel Experiment Runner with CPU Multiprocessing

Distributes parameter sweep across multiple CPU cores.
Each worker can use GPU acceleration for individual simulations.
"""

import multiprocessing as mp
from multiprocessing import Pool
import itertools
from typing import List, Dict, Any, Callable
import time
import sys
from datetime import datetime, timedelta


class ParallelExperimentRunner:
    """
    Run parameter sweeps in parallel using multiprocessing.

    Combines CPU-level parallelism (multiple workers) with
    GPU acceleration (within each worker).
    """

    def __init__(self, num_workers: int = None):
        """
        Initialize parallel runner.

        Args:
            num_workers: Number of parallel workers (None = auto-detect)
        """
        if num_workers is None:
            # Use fewer workers to reduce memory pressure and IPC overhead
            # 8-12 workers is optimal for most systems
            num_workers = min(12, max(4, mp.cpu_count() // 2))

        self.num_workers = num_workers
        print(f"Parallel runner initialized with {num_workers} workers")

    def run_parameter_sweep(self, simulation_func: Callable,
                             parameter_grid: List[Dict[str, Any]],
                             progress_callback: Callable = None) -> List[Any]:
        """
        Run parameter sweep in parallel.

        Args:
            simulation_func: Function to run for each parameter set
                             Should accept **kwargs and return result dict
            parameter_grid: List of parameter dictionaries
            progress_callback: Optional callback for progress updates

        Returns:
            List of results from all simulations
        """
        total = len(parameter_grid)
        print(f"Running {total} simulations across {self.num_workers} workers...")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        sys.stdout.flush()

        start_time = time.time()
        results = []
        completed = 0
        last_update = 0

        # Create process pool
        with Pool(processes=self.num_workers) as pool:
            # Map parameters to simulations
            async_results = []
            for params in parameter_grid:
                async_result = pool.apply_async(simulation_func, kwds=params)
                async_results.append(async_result)

            # Collect results with progress tracking
            print("Progress: [", end='', flush=True)

            for i, async_result in enumerate(async_results):
                try:
                    result = async_result.get(timeout=600)  # 10 min timeout per sim
                    if result is not None:
                        results.append(result)
                    completed += 1

                    # Visual progress dot every 1% or every 8 completions
                    dot_interval = max(1, total // 100)
                    if completed % dot_interval == 0 or completed == total:
                        print('.', end='', flush=True)

                    # Detailed progress update every 5% or 40 completions
                    update_interval = max(1, total // 20)
                    if completed % update_interval == 0 or completed == total:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        remaining_sims = total - completed
                        eta_seconds = remaining_sims / rate if rate > 0 else 0
                        eta_str = str(timedelta(seconds=int(eta_seconds)))

                        percent = completed * 100 // total

                        print(f"\n  {completed}/{total} ({percent}%) | "
                              f"Rate: {rate:.2f} sim/s | "
                              f"ETA: {eta_str}", end='', flush=True)
                        print("\n  [", end='', flush=True)

                    # Optional callback
                    if progress_callback:
                        progress_callback(completed, total, result)

                except Exception as e:
                    print(f"\n  Error in simulation {i}: {e}", flush=True)
                    print("  [", end='', flush=True)
                    completed += 1

            print("]", flush=True)

        elapsed = time.time() - start_time
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        print(f"Successful runs: {len(results)}/{total}")

        return results


def build_parameter_grid(num_sources_list: List[int],
                          geometries: List[str],
                          phase_offsets: List[int],
                          time_horizons: List[float],
                          gamma_values: List[float],
                          alpha_0_values: List[float],
                          dimension: int,
                          grid_sizes: tuple,
                          alpha_1: float = 0.0,
                          M: int = 1) -> List[Dict[str, Any]]:
    """
    Build parameter grid for dimensional experiments.

    Returns list of parameter dictionaries ready for parallel execution.
    """
    parameter_grid = []

    for num_sources, geometry, phase_offset, T, gamma, alpha_0 in itertools.product(
        num_sources_list, geometries, phase_offsets, time_horizons, gamma_values, alpha_0_values
    ):
        params = {
            'num_sources': num_sources,
            'geometry': geometry,
            'phase_offset': phase_offset,
            'T': T,
            'gamma': gamma,
            'alpha_0': alpha_0,
            'dimension': dimension,
            'grid_sizes': grid_sizes,
            'alpha_1': alpha_1,
            'M': M,
        }
        parameter_grid.append(params)

    return parameter_grid


def run_single_experiment(num_sources: int, geometry: str, phase_offset: int,
                           T: float, gamma: float, alpha_0: float,
                           dimension: int, grid_sizes: tuple,
                           alpha_1: float = 0.0, M: int = 1) -> Dict[str, Any]:
    """
    Run a single experiment (to be called by parallel workers).

    This function will be pickled and sent to worker processes,
    so it must import dependencies internally.
    """
    # Import here to avoid pickling issues
    from gpu_wave_solver import (
        run_gpu_simulation,
        create_symmetric_config_nd,
        create_clustered_config_nd
    )

    # Create config
    if geometry == 'symmetric':
        config = create_symmetric_config_nd(num_sources, dimension, 1.0, alpha_0)
    else:
        config = create_clustered_config_nd(num_sources, dimension, 1.0, alpha_0)

    # Apply phase
    if phase_offset == 1 and num_sources > 1:
        config.phases = [i % 2 for i in range(num_sources)]

    # Run GPU simulation
    result = run_gpu_simulation(config, dimension, grid_sizes, alpha_0, alpha_1, gamma, M, T)

    if result is None:
        return None

    # Add experiment metadata
    result['parameters']['geometry'] = geometry
    result['parameters']['phase_offset'] = phase_offset

    return result


if __name__ == "__main__":
    print("Testing parallel experiment runner...")

    # Small test: 2D with reduced parameters
    parameter_grid = build_parameter_grid(
        num_sources_list=[1, 2],
        geometries=['symmetric'],
        phase_offsets=[0],
        time_horizons=[100.0],
        gamma_values=[0.001],
        alpha_0_values=[1.0, 2.0],
        dimension=2,
        grid_sizes=(64, 64),
        alpha_1=0.0,
        M=1
    )

    print(f"Test grid: {len(parameter_grid)} simulations")

    runner = ParallelExperimentRunner(num_workers=2)
    results = runner.run_parameter_sweep(run_single_experiment, parameter_grid)

    print(f"\nTest complete: {len(results)} results collected")
    for r in results:
        if r:
            p = r['parameters']
            s = r['statistics']
            print(f"  {p['num_sources']} sources, alpha_0={p['alpha_0']:.1f}: "
                  f"{s['agent_commit_count']} commits")
