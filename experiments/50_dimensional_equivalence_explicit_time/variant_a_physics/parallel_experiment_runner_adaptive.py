"""
Parallel Experiment Runner with CPU Multiprocessing - Adaptive Timeout Version

Distributes parameter sweep across multiple CPU cores.
Timeout adapts based on simulation time horizon T.
Supports checkpointing and early-stop conditions.
"""

import multiprocessing as mp
from multiprocessing import Pool
import itertools
from typing import List, Dict, Any, Callable, Set, Tuple
import time
import sys
from datetime import datetime, timedelta


class ParallelExperimentRunner:
    """Run parameter sweeps in parallel with adaptive timeouts."""

    def __init__(self, num_workers: int = None):
        if num_workers is None:
            num_workers = min(12, max(4, mp.cpu_count() // 2))
        self.num_workers = num_workers
        print(f"Parallel runner initialized with {num_workers} workers (adaptive timeout)")

    def run_parameter_sweep(self, simulation_func: Callable,
                             parameter_grid: List[Dict[str, Any]],
                             progress_callback: Callable = None,
                             completed_run_ids: Set[int] = None,
                             early_stop_params: Dict[str, Any] = None) -> Tuple[List[Any], bool]:
        """
        Run parameter sweep in parallel with checkpointing and early-stop.

        Args:
            simulation_func: Function to run for each parameter set
            parameter_grid: List of parameter dictionaries
            progress_callback: Optional callback(completed, total, result, run_id)
            completed_run_ids: Set of already completed run IDs (for resume)
            early_stop_params: Dict with 'max_error_density' and 'max_consecutive_timeouts'

        Returns:
            (results, stopped_early): List of results and bool indicating early stop
        """
        if completed_run_ids is None:
            completed_run_ids = set()

        if early_stop_params is None:
            early_stop_params = {
                'max_error_density': 1.0,  # 100% (no limit)
                'max_consecutive_timeouts': 999999
            }

        # Add run_id to each parameter set
        for i, params in enumerate(parameter_grid):
            params['run_id'] = i

        # Filter out completed runs
        remaining_grid = [p for p in parameter_grid if p['run_id'] not in completed_run_ids]

        total = len(parameter_grid)
        remaining = len(remaining_grid)

        print(f"Running {remaining}/{total} simulations across {self.num_workers} workers...")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        sys.stdout.flush()

        start_time = time.time()
        results = [None] * total  # Pre-allocate with None for all runs
        completed = len(completed_run_ids)
        errors = 0
        consecutive_timeouts = 0
        stopped_early = False

        with Pool(processes=self.num_workers) as pool:
            # Store params with async_result for adaptive timeout
            async_results = []
            for params in remaining_grid:
                async_result = pool.apply_async(simulation_func, kwds=params)
                async_results.append((async_result, params))

            print("Progress: [", end='', flush=True)

            for i, (async_result, params) in enumerate(async_results):
                run_id = params['run_id']
                error_occurred = False

                try:
                    # Adaptive timeout: max(10 min, 2x time horizon)
                    T = params.get('T', 100.0)
                    timeout_seconds = max(600, int(T * 2))
                    result = async_result.get(timeout=timeout_seconds)

                    if result is not None:
                        result['run_id'] = run_id
                        results[run_id] = result
                        consecutive_timeouts = 0  # Reset on success
                    else:
                        error_occurred = True
                        errors += 1
                        consecutive_timeouts += 1

                    completed += 1

                    # Visual progress
                    dot_interval = max(1, remaining // 100)
                    if (i + 1) % dot_interval == 0 or (i + 1) == remaining:
                        print('.', end='', flush=True)

                    # Detailed progress update
                    update_interval = max(1, remaining // 20)
                    if (i + 1) % update_interval == 0 or (i + 1) == remaining:
                        elapsed = time.time() - start_time
                        rate = (i + 1) / elapsed if elapsed > 0 else 0
                        remaining_sims = remaining - (i + 1)
                        eta_seconds = remaining_sims / rate if rate > 0 else 0
                        eta_str = str(timedelta(seconds=int(eta_seconds)))
                        percent = completed * 100 // total
                        error_density = errors / completed if completed > 0 else 0

                        print(f"\n  {completed}/{total} ({percent}%) | "
                              f"Rate: {rate:.2f} sim/s | "
                              f"Errors: {errors} ({error_density*100:.2f}%) | "
                              f"Consecutive timeouts: {consecutive_timeouts} | "
                              f"ETA: {eta_str}", end='', flush=True)
                        print("\n  [", end='', flush=True)

                    # Progress callback with run_id
                    if progress_callback:
                        progress_callback(completed, total, result, run_id)

                    # Early stop checks
                    if completed >= 50:  # Only check after 50 runs for stable statistics
                        error_density = errors / completed

                        if error_density > early_stop_params['max_error_density']:
                            print(f"\n\n  EARLY STOP: Error density {error_density*100:.2f}% exceeds "
                                  f"threshold {early_stop_params['max_error_density']*100:.2f}%", flush=True)
                            stopped_early = True
                            break

                        if consecutive_timeouts >= early_stop_params['max_consecutive_timeouts']:
                            print(f"\n\n  EARLY STOP: {consecutive_timeouts} consecutive timeouts exceeds "
                                  f"threshold {early_stop_params['max_consecutive_timeouts']}", flush=True)
                            stopped_early = True
                            break

                except Exception as e:
                    print(f"\n  Error in simulation {run_id}: {e}", flush=True)
                    print("  [", end='', flush=True)
                    error_occurred = True
                    errors += 1
                    consecutive_timeouts += 1
                    completed += 1

                    if progress_callback:
                        progress_callback(completed, total, None, run_id)

            print("]", flush=True)

        elapsed = time.time() - start_time
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        print(f"Successful runs: {len([r for r in results if r is not None])}/{total}")
        print(f"Failed runs: {errors}/{total} ({errors/total*100:.2f}%)")

        return results, stopped_early


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
                           alpha_1: float = 0.0, M: int = 1,
                           run_id: int = -1) -> Dict[str, Any]:
    from gpu_wave_solver import (
        run_gpu_simulation,
        create_symmetric_config_nd,
        create_clustered_config_nd
    )

    if geometry == 'symmetric':
        config = create_symmetric_config_nd(num_sources, dimension, 1.0, alpha_0)
    else:
        config = create_clustered_config_nd(num_sources, dimension, 1.0, alpha_0)

    if phase_offset == 1 and num_sources > 1:
        config.phases = [i % 2 for i in range(num_sources)]

    result = run_gpu_simulation(config, dimension, grid_sizes, alpha_0, alpha_1, gamma, M, T)

    if result is None:
        return None

    result['parameters']['geometry'] = geometry
    result['parameters']['phase_offset'] = phase_offset
    result['run_id'] = run_id

    return result
