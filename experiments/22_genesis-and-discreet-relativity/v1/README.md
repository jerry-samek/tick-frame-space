# Tick-Frame Observer Architecture v1

**Experiment 22: Genesis and Discrete Relativity**

This implementation provides a modular substrate engine with observer pattern for running tick-frame physics experiments.

## Architecture Overview

### Core Principles

- **One shared substrate engine** - Minimal state representation
- **Many independent observers** - Compute derived quantities without modifying substrate
- **Experiments are configurations** - Not separate engines

### Key Components

1. **SubstrateState** (`substrate.py`)
   - Minimal representation: entities, adjacency graph, tick counter
   - Geometry-free, no coordinates, only adjacency

2. **UpdateRule** (`substrate.py`)
   - Abstract class defining substrate evolution
   - Methods: `expand()`, `mutate()`, `bias()`, `step()`
   - Local, memoryless, synchronous transformations

3. **SubstrateEngine** (`substrate.py`)
   - Runs ticks and notifies observers
   - Holds current state
   - Manages observer lifecycle

4. **Observer Base** (`observers/base.py`)
   - Abstract observer interface
   - Hooks: `on_pre_tick()`, `on_post_tick()`
   - Logging utilities: CSV, JSON, text

5. **Observers** (`observers/*.py`)
   - **GenesisObserver**: Adjacency frontier, density, horizon
   - **RelativityObserver**: Worldlines, causal classification
   - **PiDriftObserver**: Adjacency shells, π(t,R)
   - **ConstantsDriftObserver**: α(t), G(t), h(t), Λ(t)
   - **EntropyObserver**: Reachable states, S(t)
   - **ParticleObserver**: Adjacency loops, identity stability
   - **ForceCollapseObserver**: Adjacency bias signatures

6. **ExperimentConfig** (`experiment.py`)
   - Configuration dataclass
   - Bundles: initial state, update rule, observers, parameters

## Installation

```bash
cd experiments/22_genesis-and-discreet-relativity/v1
pip install -r requirements.txt
```

## Quick Start

### Running the Example Experiment

```bash
python run_experiment.py
```

This runs a simple random evolution experiment with all observers enabled.

### Creating a Custom Update Rule

```python
from substrate import UpdateRule, SubstrateState

class MyUpdateRule(UpdateRule):
    def expand(self, state: SubstrateState) -> SubstrateState:
        # Add new entities or edges
        return state

    def mutate(self, state: SubstrateState) -> SubstrateState:
        # Modify existing adjacency
        return state

    def bias(self, state: SubstrateState) -> SubstrateState:
        # Apply asymmetric transformations
        return state
```

### Configuring an Experiment

```python
from experiment import ExperimentConfig, run_experiment
from observers import GenesisObserver, EntropyObserver

config = ExperimentConfig(
    name="My Experiment",
    description="Testing custom update rule",
    initial_state_builder=lambda: create_simple_initial_state(10, 15),
    update_rule=MyUpdateRule(),
    observers=[
        GenesisObserver(log_interval=10, output_dir="./output"),
        EntropyObserver(log_interval=10, output_dir="./output"),
    ],
    max_ticks=100,
)

engine = run_experiment(config)
```

## Observer Outputs

Each observer writes CSV files to the `results/` directory:

- `genesis_metrics.csv` - Entity counts, density, frontier, horizon
- `relativity_metrics.csv` - Worldlines, causal classification
- `pi_drift_shells.csv` - Shell populations, π estimates
- `constants_drift.csv` - Emergent constants: α, G, h, Λ
- `entropy_metrics.csv` - Degree entropy, complexity
- `particle_metrics.csv` - Cycles, stable entities, triangles
- `force_collapse_metrics.csv` - Bias signatures, edge asymmetry

Text logs are also written to `.txt` files for quick summaries.

All output files are located in `v1/results/` after running the experiment.

## Customization Guide

### 1. Implement Your Update Rule

The `UpdateRule` class has three phases you can customize:

- **expand()**: Add new entities or edges (growth)
- **mutate()**: Modify existing adjacency (dynamics)
- **bias()**: Apply asymmetric transformations (emergence of structure)

The `step()` method executes them in sequence: expand → mutate → bias.

### 2. Choose Initial State

Three builders are provided:

```python
create_simple_initial_state(num_entities=10, num_edges=15)  # Random graph
create_ring_initial_state(num_entities=10)  # Ring topology
create_star_initial_state(num_satellites=9)  # Star topology
```

Or create your own:

```python
def my_initial_state():
    state = SubstrateState()
    # Add entities
    state.entities[0] = {}
    state.entities[1] = {}
    # Add edges
    state.adjacency.add_edge(0, 1)
    return state
```

### 3. Select Observers

Choose which observers to attach based on what you want to measure:

- **Genesis** - Basic growth metrics
- **Relativity** - Temporal coherence
- **PiDrift** - Geometric properties
- **Constants** - Emergent coupling strengths
- **Entropy** - Complexity measures
- **Particle** - Stable structures
- **ForceCollapse** - Bias detection

You can attach all or just a subset.

### 4. Create Custom Observers

```python
from observers.base import Observer

class MyObserver(Observer):
    def __init__(self, log_interval=1, output_dir=None):
        super().__init__(name="MyObserver", log_interval, output_dir)

    def on_post_tick(self, state):
        # Compute your metrics
        my_metric = some_computation(state.adjacency)

        # Log if needed
        if self.should_log(state.tick):
            self.log_csv('my_metrics.csv', {
                'tick': state.tick,
                'my_metric': my_metric,
            })
```

## Project Structure

```
v1/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Excludes results/ from git
├── substrate.py                   # Core substrate engine
├── experiment.py                  # Configuration and runner
├── run_experiment.py              # Example experiment
├── results/                       # Output directory (created on first run)
│   ├── *.csv                      # Observer metrics
│   └── *.txt                      # Observer logs
└── observers/
    ├── __init__.py
    ├── base.py                    # Observer base class
    ├── genesis.py                 # Genesis metrics
    ├── relativity.py              # Relativity metrics
    ├── pi_drift.py                # Pi drift metrics
    ├── constants_drift.py         # Constants metrics
    ├── entropy.py                 # Entropy metrics
    ├── particle.py                # Particle metrics
    └── force_collapse.py          # Force collapse metrics
```

## Next Steps

1. **Implement your update rule** - Edit `run_experiment.py` or create a new file
2. **Run experiments** - Execute `python run_experiment.py`
3. **Analyze outputs** - Check CSV files in the output directory
4. **Iterate** - Refine your update rule based on observer data

## Theory Background

See `../Experiment Architecture.md` for the theoretical foundation of this architecture.

Key concepts:
- **Substrate**: Minimal graph state (entities + adjacency)
- **Update Rule**: Local, memoryless transformation A(t+1) = U(A(t))
- **Observers**: Read-only metric computers
- **Experiments**: Configurations, not code

## License

Part of the Tick-Frame Space research project.
