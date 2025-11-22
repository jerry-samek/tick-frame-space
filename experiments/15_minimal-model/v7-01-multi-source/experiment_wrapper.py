"""
Wrapper for v6-gpu run_single_experiment to work with v7 adaptive parallel runner.

The v6-gpu function returns results with parameters nested in result['parameters'],
but v7 progress callbacks expect parameters at the top level for easy access.
"""

from typing import Dict, Any
from experiment_utils import run_single_experiment as v6_run_single_experiment


def run_single_experiment_v7(num_sources: int, geometry: str, phase_offset: int,
                              T: float, gamma: float, alpha_0: float,
                              dimension: int, grid_sizes: tuple,
                              alpha_1: float = 0.0, M: int = 1, run_id=None) -> Dict[str, Any]:
    """
    Wrapper that calls v6-gpu run_single_experiment and enhances the result.

    Args:
        num_sources: Number of wave sources
        geometry: 'symmetric' or 'clustered'
        phase_offset: Phase offset (0 or 1)
        T: Time horizon
        gamma: Damping coefficient
        alpha_0: Field strength
        dimension: Spatial dimension (1-5)
        grid_sizes: Grid size tuple
        alpha_1: Secondary field parameter
        M: Threshold parameter
        run_id: Run identifier (optional, for tracking)

    Returns:
        Enhanced result dictionary with parameters promoted to top level
    """
    # Call v6-gpu function (it doesn't accept run_id)
    result = v6_run_single_experiment(
        num_sources=num_sources,
        geometry=geometry,
        phase_offset=phase_offset,
        T=T,
        gamma=gamma,
        alpha_0=alpha_0,
        dimension=dimension,
        grid_sizes=grid_sizes,
        alpha_1=alpha_1,
        M=M
    )

    if result is None:
        return None

    # Promote key parameters to top level for progress callback
    result['num_sources'] = num_sources
    result['geometry'] = geometry
    result['phase_offset'] = phase_offset
    result['T'] = T
    result['gamma'] = gamma
    result['alpha_0'] = alpha_0
    result['dimension'] = dimension
    result['grid_sizes'] = grid_sizes
    result['alpha_1'] = alpha_1
    result['M'] = M

    if run_id is not None:
        result['run_id'] = run_id

    return result
