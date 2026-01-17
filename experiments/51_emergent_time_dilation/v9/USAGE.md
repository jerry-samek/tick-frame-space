# Experiment 51i (V9) - Usage Guide

Quick start guide for running the multi-entity gravitational-relativistic time dilation experiment.

---

## Quick Start

### 1. Run Single Configuration

Run the baseline configuration with full analysis pipeline:

```bash
python run_analysis.py baseline
```

This will:
- Load the baseline configuration
- Run 5000 ticks of simulation
- Validate results against success criteria
- Generate all visualizations
- Export analysis CSV

**Output**: `results_baseline/` directory with:
- `baseline_dashboard.png` - Comprehensive 7-panel summary
- `baseline_gamma_field.png` - Time dilation heatmap
- `baseline_fields.png` - Load and energy fields
- `baseline_trajectories.png` - Entity paths through field
- `baseline_gamma_distance.png` - Gradient validation
- `baseline_gamma_velocity.png` - Lorentz factor validation
- `baseline_animation.gif` - Animated simulation (optional)
- `baseline_analysis.csv` - Detailed per-entity data

### 2. Run Experiment Only

For faster testing without visualizations:

```bash
python experiment_51i.py baseline
```

### 3. Compare Configurations

Compare multiple parameter sets:

```bash
python run_analysis.py compare baseline strong_field weak_field
```

**Output**: Comparison table showing which configurations pass validation.

---

## Available Configurations

Use these configuration names with `run_analysis.py` or `experiment_51i.py`:

| Configuration | Description | Key Parameters |
|--------------|-------------|----------------|
| `baseline` | Goldilocks parameters (recommended) | α=0.012, γ=0.0005, scale=0.75 |
| `strong_field` | Stronger gravitational field | α=0.011, γ=0.0007, scale=0.85 |
| `weak_field` | Weaker gravitational field | α=0.014, γ=0.0003, scale=0.65 |
| `fast_motion` | More high-velocity entities | 8 per velocity, v_ultra=0.995c |
| `dense_planet` | Denser planet cluster | 1500 entities, r=8.0 |

---

## Module Structure

```
v9/
├── config.py              # Parameter configurations
├── entity_motion.py       # MovingEntity, trajectory generators
├── field_dynamics.py      # Load/energy field dynamics
├── experiment_51i.py      # Main simulation loop
├── analysis.py            # Time dilation decomposition
├── visualize.py           # Static and animated plots
└── run_analysis.py        # Complete pipeline orchestration
```

### Module Usage

**Config**:
```python
from config import get_config, list_configurations

# List available configs
print(list_configurations())

# Load config
config = get_config("baseline")
print(config.summary())
```

**Experiment**:
```python
from experiment_51i import Experiment51i
from config import get_config

config = get_config("baseline")
experiment = Experiment51i(config)
experiment.run()
experiment.print_results()
```

**Analysis**:
```python
from analysis import validate_experiment, analyze_entity_time_dilation

# Validate against success criteria
validation = validate_experiment(
    experiment.mobile_entities,
    planet_center=(50.0, 50.0),
    verbose=True
)

# Decompose single entity
decomp = analyze_entity_time_dilation(
    experiment.mobile_entities[0],
    planet_center=(50.0, 50.0)
)
print(f"Measured: γ={decomp.gamma_eff_measured:.3f}")
print(f"Predicted: γ_grav={decomp.gamma_grav_avg:.3f} × γ_SR={decomp.gamma_SR_avg:.3f}")
```

**Visualization**:
```python
from visualize import plot_summary_dashboard, plot_gamma_field

# Create dashboard
plot_summary_dashboard(
    experiment.mobile_entities,
    experiment.fields,
    planet_center=(50.0, 50.0),
    save_path="dashboard.png"
)

# Individual plots
plot_gamma_field(
    experiment.fields,
    planet_center=(50.0, 50.0),
    save_path="gamma.png"
)
```

---

## Custom Configuration

Create custom configurations programmatically:

```python
from config import ConfigurationSet, FieldParameters, EntityConfiguration, SimulationParameters

custom_config = ConfigurationSet(
    name="my_experiment",
    field=FieldParameters(
        alpha=0.013,
        gamma_damp=0.0004,
        scale=0.8,
        R=1.3,
        E_max=18.0
    ),
    entities=EntityConfiguration(
        planet_count=1000,
        planet_radius=12.0,
        mobile_count_per_velocity=10,
        v_slow=0.2,
        v_moderate=0.6,
        v_fast=0.95,
        v_ultra=0.999
    ),
    simulation=SimulationParameters(
        grid_size=150,
        num_ticks=10000,
        snapshot_interval=200
    )
)

experiment = Experiment51i(custom_config)
experiment.run()
```

---

## Parameter Sweeps

Generate parameter sweep configurations:

```python
from config import parameter_sweep_configs, baseline_config

# Sweep alpha parameter
configs = parameter_sweep_configs(
    base_config=baseline_config(),
    param_name='alpha',
    values=[0.010, 0.012, 0.014, 0.016]
)

# Run all configurations
for config in configs:
    experiment = Experiment51i(config)
    experiment.run()
    # ... analyze results
```

---

## Understanding the Output

### Success Criteria

The experiment validates 5 criteria:

1. **Gravitational Gradient**: γ_grav decreases monotonically with distance
2. **Velocity Effects Match SR**: γ_SR = 1/√(1-v²/c²) within 10% error
3. **Effects Multiply**: γ_total ≈ γ_grav × γ_SR within 15% error
4. **Stable Equilibrium**: No collapse (γ > 0.5) or runaway (γ < 100)
5. **Smooth Fields**: Standard deviation of γ within bins < 0.5

**Pass threshold**: All 5 criteria must pass.

### Validation Output

```
VALIDATION REPORT
======================================================================

Overall Status: PASS

Success Criteria:
  ✓ 1 Gravitational Gradient
  ✓ 2 Velocity Effects Match Sr
  ✓ 3 Effects Multiply
  ✓ 4 Stable Equilibrium
  ✓ 5 Smooth Fields

Velocity Regime Analysis:
Regime       Count  γ_eff    γ_grav   γ_SR     Error    Pass
----------------------------------------------------------------------
slow         5      1.523    1.502    1.015    2.34%    ✓
moderate     5      1.753    1.485    1.155    3.12%    ✓
fast         5      3.421    1.462    2.294    2.87%    ✓
ultra        5      10.234   1.445    7.089    1.45%    ✓
```

### Interpreting Results

**Measured Time Dilation**:
- `proper_time`: Time experienced by entity (τ)
- `coordinate_time`: Substrate ticks elapsed (t)
- `gamma_eff_measured`: t/τ (>1.0 means time dilation)

**Predicted Components**:
- `gamma_SR_avg`: Special relativistic contribution from velocity
- `gamma_grav_avg`: Gravitational contribution from field
- `gamma_total_predicted`: γ_SR × γ_grav

**Validation**:
- `relative_error`: |γ_predicted - γ_measured| / γ_measured
- `passes_threshold`: Error < 15%

---

## Performance

**Baseline configuration timing**:
- 5000 ticks simulation: ~120-180 seconds
- Analysis: ~2-5 seconds
- Visualizations: ~10-15 seconds
- Animation (50 frames): ~30-60 seconds

**Memory**: ~500 MB for baseline (700 planet entities + 20 mobile)

**Scaling**:
- Linear in grid size (100×100 default)
- Linear in planet count
- Negligible impact from mobile entity count (<100)

---

## Dependencies

Required Python packages:

```bash
pip install numpy scipy matplotlib
```

**Versions tested**:
- Python 3.8+
- numpy >= 1.20
- scipy >= 1.7
- matplotlib >= 3.4

---

## Troubleshooting

**Import errors**:
- Ensure all modules are in the same directory
- Python module names can't start with digits (experiment_51i.py, not 51i_experiment.py)

**Slow performance**:
- Reduce `num_ticks` in config (e.g., 1000 for quick tests)
- Reduce `grid_size` (e.g., 80×80)
- Reduce `planet_count`
- Skip animation generation

**Memory issues**:
- Reduce snapshot_interval (saves less history)
- Reduce planet_count
- Use smaller grid_size

**Animation fails**:
- Requires Pillow: `pip install Pillow`
- May need ffmpeg for MP4 output

**Validation fails**:
- Check parameter ranges are reasonable
- Ensure num_ticks is sufficient (≥5000 recommended)
- Try baseline config first to verify installation

---

## Next Steps

1. **Run baseline**: Validate installation and understand output
2. **Try configurations**: Compare strong_field vs weak_field
3. **Custom parameters**: Tune to match specific physics targets
4. **Parameter sweeps**: Systematic exploration of parameter space
5. **Theory validation**: Compare results to GR/SR predictions

---

## References

- **Theory**: `../README.md` - Full experimental design
- **Experimental Arc**: `../EXPERIMENTAL_ARC.md` - V1-V8 journey
- **Theory Docs**: `../../../docs/theory/` - Tick-frame physics foundation

---

**Status**: COMPLETE - All modules implemented and tested
**Last Updated**: January 2026
