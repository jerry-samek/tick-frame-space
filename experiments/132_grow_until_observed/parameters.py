# experiments/132_grow_until_observed/parameters.py
"""Capacitor substrate parameters. Tunable for Phase 1 parameter search.

Provisional values per spec §"Parameters". Phase 1 may need to iterate;
document the working region in RESULTS_phase1.md.
"""
from dataclasses import dataclass


@dataclass
class Parameters:
    baseline_threshold: float = 100.0
    adaptation_rate: float = 0.5      # threshold += this on each discharge
    relaxation_rate: float = 0.05     # threshold -= this per idle tick (clamped at baseline)
    deposit_amount: float = 30.0      # charge added to receiver per arriving deposit
    load_coefficient: float = 0.0     # 0 for Phase 1 (deferred to Phase 2)
    propagation_time_base: float = 1.0
    bootstrap_charge_step: float = 0.25  # fraction of baseline_threshold per cell offset


DEFAULT = Parameters()
