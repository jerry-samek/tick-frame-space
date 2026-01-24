# A Deterministic, Tick-Frame-Based Cellular Automaton Framework for the Double-Slit Experiment: Formalization, Dynamics, and Theoretical Predictions

---

## Introduction

The double-slit experiment remains a central pillar in the conceptual and experimental foundations of quantum mechanics, vividly illustrating the phenomena of interference, superposition, and measurement-induced collapse. Since its inception by Thomas Young and its subsequent reinterpretation for electrons and other quantum particles, the experiment has been a touchstone for debates on the nature of reality, determinism, and the measurement problem (Feynman 1965; Dirac 1930; Bohm 1952). The standard quantum mechanical (QM) description employs the wavefunction formalism, invoking superposition and probabilistic collapse upon measurement, as codified in the Copenhagen interpretation and further formalized by Dirac and von Neumann. However, alternative approaches—including Bohmian mechanics, pilot-wave theories, and more recently, deterministic cellular automaton (CA) models—have sought to provide a realist, possibly deterministic, underpinning to quantum phenomena.

This report develops a formal scientific experimental framework for a deterministic, tick-frame-based reinterpretation of the double-slit experiment. The model assumes that the electron is not a point particle nor a delocalized wave, but a distributed structure composed of discrete 'broks'—localized excitations—within a cellular automaton-like substrate. Emission is triggered by a gamma-field impulse that disrupts atomic binding, releasing the electron as a dispersing shrapnel-like cloud of broks. As these broks propagate, they interact with structured gamma fields along the slit edges, leading to deterministic but highly sensitive trajectory evolution. Measurement is modeled as a second gamma impulse that collapses the broks into a single macroscopic outcome. This framework is situated within the context of foundational quantum mechanics literature and is compared in detail to standard QM expectations, pilot-wave/Bohmian mechanics, and recent CA-based models.

---

## Formal Description of Model Entities

### The Electron as a Brok-Distributed Structure

In this framework, the **electron** is conceptualized not as a point-like particle nor as a continuous wavefunction, but as a **cloud of discrete, localized excitations**—termed **broks**—embedded within a cellular automaton (CA) substrate. Each brok represents a localized, quantized excitation of the substrate, analogous to a "cellular" excitation in CA models of physical systems. The electron's state at any tick (discrete time step) is given by the set of positions and internal states of its constituent broks.

Mathematically, the electron's state can be represented as:
\[
E(t) = \{ (r_i, s_i) \mid i = 1, ..., N_b \}
\]
where \( r_i \) is the position of the \( i \)-th brok in the CA lattice, \( s_i \) its internal state, and \( N_b \) the total number of broks comprising the electron at time \( t \).

This approach is inspired by both the **particle-based representations in deterministic models** (e.g., Chertock 2021; 't Hooft 2016) and the **distributed, extended-object models** found in recent double-slit reinterpretations (Tsai & Hong 2025; Rahman 2024).

### The Gamma Field and Gamma Impulses

The **gamma field** is a structured, dynamic field defined over the CA substrate, capable of mediating both emission and measurement events. It is modeled as a set of field values \( \Gamma(r, t) \) defined at each cell \( r \) and tick \( t \), with structured spatial and temporal profiles.

- **Emission Gamma Impulse**: A localized, high-intensity gamma field fluctuation that disrupts atomic binding, releasing the electron as a brok cloud.
- **Measurement Gamma Impulse**: A second, spatially extended gamma field fluctuation that interacts with the brok cloud, inducing collapse into a localized, macroscopic outcome.

The gamma field is analogous to the **external control fields** in open quantum systems and the **potential landscape** in CA models, but here it plays an active, deterministic role in both emission and measurement.

### The Cellular Automaton Substrate

The **substrate** is a **cellular automaton**: a discrete, regular lattice of cells, each with a finite set of possible states, evolving synchronously in discrete time steps (ticks) according to local update rules. The CA substrate provides the ontological basis for all entities and dynamics in the model.

Formally, the CA is defined as a tuple \( (A, \Psi, R, \mathcal{N}) \) where:
- \( A \): Regular lattice of cells in \( d \)-dimensional space.
- \( \Psi(r, t) \): Set of state variables at cell \( r \) and time \( t \).
- \( R \): Set of local update rules, applied synchronously to all cells.
- \( \mathcal{N} \): Neighborhood structure (e.g., Moore or von Neumann neighborhood).

The CA substrate supports the propagation of broks, the evolution of the gamma field, and the implementation of boundary conditions (e.g., slit geometry).

---

## Tick-Frame Dynamics and Time Discretization

### Discrete Time Evolution

Time in the model is **discretized into ticks**: each tick corresponds to a global update of all CA cells. The evolution of the system is thus a sequence of CA configurations indexed by tick number \( n \).

- **Tick-Frame**: The fundamental unit of time, during which all cells update their states synchronously.
- **Deterministic Update**: The state of each cell at tick \( n+1 \) is a deterministic function of its own state and the states of its neighbors at tick \( n \), possibly also influenced by the gamma field.

This discretization is essential for both the **computational implementation** and the **physical interpretation** of the model, aligning with the CA interpretation of quantum mechanics (’t Hooft 2016).

### State Representation and Observables

The **state of the system** at tick \( n \) is given by the configuration of all CA cells, including the positions and states of broks, the gamma field values, and any boundary or measurement markers.

Observables (e.g., detection events, interference patterns) are defined as **macroscopic functions** of the CA configuration, typically involving spatial or temporal aggregation over many ticks or cells.

---

## Experimental Phases: Step-by-Step Breakdown

The deterministic CA-based double-slit experiment is structured into four principal phases: emission, propagation, interaction with slits, and measurement. Each phase is formally defined below, with explicit reference to the model entities and tick-frame dynamics.

### 1. Emission Phase: Gamma Impulse Disrupting Atomic Binding

**Physical Picture**: The electron is initially bound within an atom, represented as a localized, stable configuration of broks within the CA substrate. Emission is triggered by a **gamma-field impulse**—a localized, high-intensity fluctuation in the gamma field—that disrupts the atomic binding, releasing the electron as a dispersing brok cloud.

**Formal Steps**:
- At tick \( n_0 \), a gamma impulse \( \Gamma_{emit}(r, n_0) \) is applied at the emission site \( r_0 \).
- The local CA update rules at \( r_0 \) and its neighborhood are modified to reflect the energy input, causing the bound broks to transition into a **dispersed, high-momentum configuration**.
- The initial state of the electron post-emission is a **shrapnel-like cloud** of broks, each with a well-defined position and velocity (direction of propagation).

**Mathematical Representation**:
\[
E(n_0^+) = \{ (r_i, s_i) \mid r_i \in \mathcal{N}(r_0), s_i = s_{emit} \}
\]
where \( s_{emit} \) encodes the high-energy, unbound state.

**Comparison to QM**: In standard QM, emission corresponds to the preparation of a wavepacket with a given momentum distribution. Here, the emission is a deterministic, localized event, with the initial conditions of the brok cloud fully specified by the CA state and the gamma impulse.

### 2. Propagation Phase: Brok Cloud Dispersion and Dynamics

**Physical Picture**: The brok cloud propagates through the CA substrate, with each brok following deterministic, local update rules. The propagation is sensitive to the local gamma field and the CA substrate's structure.

**Formal Steps**:
- For each tick \( n > n_0 \), each brok at position \( r_i \) updates its position and state according to:
  \[
  r_i(n+1) = r_i(n) + v_i(n)
  \]
  \[
  v_i(n+1) = f_{prop}(v_i(n), \Gamma(r_i(n), n), \Psi_{CA}(r_i(n), n))
  \]
  where \( f_{prop} \) is a deterministic function encoding the influence of the gamma field and substrate.
- Broks may interact with each other (e.g., via local exclusion or repulsion rules) and with the background CA state.

**Key Features**:
- **Deterministic but Sensitive**: The evolution is fully deterministic, but small differences in initial conditions or local field values can lead to divergent trajectories (sensitive dependence).
- **Distributed Structure**: The electron remains a cloud of broks, with its spatial extent and internal correlations evolving over time.

**Comparison to QM**: In QM, the wavefunction propagates according to the Schrödinger equation, spreading and interfering as it encounters obstacles. In the CA model, the brok cloud's deterministic evolution can reproduce similar spreading and interference-like patterns at the ensemble level.

### 3. Interaction with Slits: Structured Gamma Fields at Slit Edges

**Physical Picture**: As the brok cloud approaches the barrier with two slits, the **structured gamma fields** at the slit edges modulate the local CA update rules, influencing the trajectories of nearby broks.

**Formal Steps**:
- The barrier is implemented as a region of CA cells with fixed, non-propagating states (walls), except for two openings (slits) where broks can pass.
- At the slit edges, the gamma field \( \Gamma_{slit}(r, n) \) is structured to create **field gradients** or **potential steps** that interact with passing broks.
- Broks entering the slit region experience deterministic deflections or modulations in their velocities, depending on their proximity to the slit edges and the local gamma field.

**Mathematical Representation**:
\[
v_i(n+1) = f_{slit}(v_i(n), \Gamma_{slit}(r_i(n), n), \Psi_{CA}(r_i(n), n))
\]
where \( f_{slit} \) encodes the deterministic interaction with the slit geometry and field.

**Key Features**:
- **Edge Effects**: The structured gamma field at the slit edges can induce complex, sensitive trajectory changes, leading to path bifurcation and effective "interference" at the ensemble level.
- **Geometry Sensitivity**: The precise shape, width, and separation of the slits, as well as the gamma field profile, strongly influence the resulting brok trajectories.

**Comparison to QM**: In QM, the wavefunction is diffracted and interferes upon passing through the slits, with the resulting intensity pattern determined by the superposition of amplitudes from each slit. In the CA model, the deterministic evolution of the brok cloud, modulated by the slit geometry and gamma fields, can reproduce similar patterns in the distribution of detection events.

### 4. Measurement Phase: Second Gamma Impulse Collapse Mechanism

**Physical Picture**: Upon reaching the detection screen, a **second gamma impulse** is applied, representing the measurement event. This impulse interacts with the brok cloud, inducing a deterministic collapse into a single, localized macroscopic outcome (e.g., a detection event at a specific screen position).

**Formal Steps**:
- At tick \( n_{meas} \), a measurement gamma impulse \( \Gamma_{meas}(r, n_{meas}) \) is applied across the detection screen.
- The CA update rules at the screen cells and in the brok cloud are modified to implement a **collapse mechanism**: all broks are deterministically merged or funneled into a single detection event, with the outcome determined by the instantaneous configuration of the brok cloud and the gamma field.
- The measurement outcome is thus a deterministic function of the pre-measurement state, but may be highly sensitive to microscopic details.

**Mathematical Representation**:
\[
r_{det} = F_{meas}(\{ r_i(n_{meas}) \}, \Gamma_{meas}, \Psi_{CA})
\]
where \( F_{meas} \) is a deterministic, possibly chaotic function mapping the brok cloud configuration to a single detection position.

**Key Features**:
- **Deterministic Collapse**: Unlike the stochastic collapse in standard QM, the outcome is fully determined by the system's state at the moment of measurement.
- **Sensitive Dependence**: Small differences in the brok cloud configuration can lead to different measurement outcomes, enabling effective statistical behavior over many runs.

**Comparison to QM**: In standard QM, measurement induces a probabilistic collapse of the wavefunction, with outcome probabilities given by the Born rule. In the CA model, the deterministic collapse mechanism can reproduce the statistical distribution of outcomes over many runs, provided the initial conditions or environmental variables are sufficiently varied.

---

## Comparison with Standard Quantum Mechanical Expectations

### Wavefunction Superposition and Collapse

**Standard QM**: The electron is described by a complex-valued wavefunction \( \psi(r, t) \), evolving unitarily according to the Schrödinger equation. Upon measurement, the wavefunction collapses probabilistically into an eigenstate of the measured observable, with probabilities given by the Born rule.

**CA Model**: The electron is a deterministic, distributed brok cloud, evolving according to local CA rules and gamma field interactions. Measurement is a deterministic, but sensitive, collapse of the brok cloud into a single outcome.

**Key Differences**:
- **Superposition**: In QM, superposition is fundamental; in the CA model, the apparent superposition arises from the distributed nature of the brok cloud and the ensemble of possible initial conditions.
- **Collapse**: QM collapse is inherently probabilistic and non-deterministic; CA collapse is deterministic but can mimic probabilistic statistics via sensitive dependence on initial conditions.

### Interference and Pattern Formation

**Standard QM**: The interference pattern arises from the coherent superposition of wavefunction amplitudes from each slit, leading to constructive and destructive interference on the detection screen.

**CA Model**: The interference-like pattern emerges from the deterministic, but highly sensitive, evolution of the brok cloud as it interacts with the structured gamma fields at the slits. The ensemble of detection events over many runs reproduces the familiar interference fringes.

### Measurement-Induced Localization

**Standard QM**: Measurement localizes the electron to a specific position, with the probability distribution given by \( |\psi(r)|^2 \).

**CA Model**: Measurement deterministically collapses the brok cloud to a single detection event, with the outcome depending on the pre-measurement configuration. Over many runs, the distribution of outcomes can match the QM prediction, provided the initial conditions are appropriately sampled.

### Relation to Pilot-Wave and Bohmian Mechanics

The CA model shares features with **Bohmian mechanics** and **pilot-wave theories**:
- **Deterministic Trajectories**: Like Bohmian mechanics, the CA model assigns definite trajectories to the broks (analogous to Bohmian particles), guided by the local CA rules and gamma fields (analogous to the quantum potential).
- **Nonlocality and Sensitivity**: The CA substrate can encode nonlocal correlations via the gamma field and the global CA state, enabling effective nonlocality as in Bohmian mechanics.
- **Measurement**: In Bohmian mechanics, measurement outcomes are determined by the initial configuration of the particles and the guiding wave; in the CA model, outcomes are determined by the brok cloud configuration and the measurement gamma impulse.

However, the CA model differs in its **explicit discretization** and **cellular substrate**, and in the role of the gamma field as an active agent in both emission and measurement.

### Relation to Feynman Path Integral and Ensemble Trajectories

The CA model can be interpreted as a **deterministic realization of the path integral**: each brok follows a definite trajectory, and the ensemble of all possible initial conditions or environmental configurations reproduces the statistical distribution of outcomes predicted by the path integral formalism.

---

## Theoretical Predictions of the Model

### Emergence of Interference Pattern

The CA model predicts that, over many runs with varied initial conditions (e.g., emission site, brok cloud configuration, gamma field fluctuations), the **distribution of detection events on the screen** will exhibit an interference-like pattern, with fringe spacing and contrast determined by the slit geometry and gamma field structure.

- **Deterministic Origin**: Each individual run is fully deterministic, but the ensemble reproduces the statistical pattern.
- **Pattern Sensitivity**: The pattern is sensitive to the precise geometry of the slits, the profile of the gamma field at the edges, and the initial brok cloud configuration.

This prediction aligns with both standard QM and recent deterministic models (Rahman 2024; Tsai & Hong 2025; Declercq 2025).

### Sensitivity to Slit Geometry and Fields

The model predicts that **small changes in slit width, separation, or edge structure** (as encoded in the CA substrate and gamma field) will lead to **measurable changes in the interference pattern**, including fringe spacing, contrast, and overall intensity distribution.

- **Edge Effects**: The structured gamma field at the slit edges can induce asymmetries or additional features in the pattern, especially for narrow or irregular slits.
- **Field Modulation**: Varying the gamma field profile (e.g., by introducing additional field gradients or modulations) can shift or distort the pattern.

These predictions are consistent with experimental observations of slit geometry sensitivity in both optical and electron double-slit experiments.

### Measurement-Induced Localization Statistics

Although each measurement outcome is deterministic, the **distribution of outcomes over many runs** can reproduce the Born rule statistics of standard QM, provided that the initial conditions or environmental variables are sufficiently varied.

- **Statistical Reproduction**: The model can be tuned (e.g., by sampling initial brok cloud configurations from an appropriate distribution) to match the QM prediction for detection probabilities.
- **Deviation from QM**: If the initial conditions are not appropriately randomized, or if the CA substrate imposes additional constraints, deviations from the Born rule may occur, providing a potential avenue for experimental falsification.

### Decoherence and Environment Coupling in CA Substrate

The CA model naturally incorporates **decoherence** via the coupling of the brok cloud to the broader CA substrate and gamma field. Environmental perturbations (e.g., random fluctuations in the CA state or gamma field) can induce effective decoherence, suppressing interference and driving the system toward classical behavior.

- **Pointer States**: The CA substrate can select preferred basis states (pointer states) via its update rules and environmental coupling, analogous to environment-induced superselection in QM.
- **Transition to Classicality**: As decoherence increases (e.g., via stronger environmental coupling or increased noise), the interference pattern fades, and the detection statistics approach those of classical particles.

### Limitations, Assumptions, and Falsifiability Criteria

**Assumptions**:
- The CA substrate is sufficiently large and homogeneous to support the propagation of broks and gamma fields.
- The gamma field can be structured and modulated at the required spatial and temporal scales.
- The initial brok cloud configuration can be appropriately randomized or controlled.

**Limitations**:
- The model may not capture all quantum phenomena, especially those requiring entanglement or nonlocal correlations beyond the CA's capacity.
- The deterministic collapse mechanism may not reproduce all aspects of quantum measurement, particularly in complex or multi-particle systems.

**Falsifiability**:
- Deviations from the Born rule in detection statistics, under controlled initial conditions, would falsify the model.
- Failure to reproduce the observed sensitivity of the interference pattern to slit geometry or environmental decoherence would challenge the model's validity.

---

## Mathematical Formalism: State Representation and Observables

### State Space and Evolution

The **state space** of the system is the set of all possible CA configurations, including brok positions and states, gamma field values, and environmental variables.

- **State Vector**: \( S(n) = (\Psi_{CA}(r, n), \Gamma(r, n), \{ r_i, s_i \}) \)
- **Evolution**: \( S(n+1) = F(S(n)) \), where \( F \) is the global CA update function, incorporating local rules and gamma field interactions.

### Observables

- **Detection Event**: A function \( O_{det}(S(n_{meas})) \) mapping the CA state at measurement to a detection position.
- **Interference Pattern**: The histogram of detection events over many runs, \( P_{det}(x) \), compared to the QM prediction \( |\psi(x)|^2 \).

### Numerical Simulation Design and Parameter Choices

- **Lattice Size and Resolution**: The CA lattice must be large enough to accommodate the brok cloud's propagation and the barrier geometry.
- **Tick Duration**: The tick-frame duration sets the temporal resolution; must be chosen to resolve the relevant dynamics.
- **Gamma Field Profile**: The spatial and temporal structure of the gamma field at emission, slits, and measurement must be specified.
- **Initial Conditions**: The distribution of initial brok cloud configurations must be chosen to match experimental or theoretical expectations.

---

## Experimental Feasibility and Measurable Signatures

### Implementation Considerations

- **Physical Realization**: While the CA model is primarily a theoretical and computational construct, its predictions can be compared to experimental data from electron, photon, or molecule double-slit experiments.
- **Parameter Mapping**: Model parameters (e.g., brok number, gamma field strength, CA lattice spacing) must be mapped to physical quantities (e.g., electron energy, slit width, detection resolution).

### Measurable Signatures

- **Interference Pattern**: The primary observable is the spatial distribution of detection events on the screen, which can be directly compared to experimental data.
- **Pattern Sensitivity**: Systematic variation of slit geometry or environmental conditions can test the model's predictions for pattern changes.
- **Decoherence Effects**: Introducing controlled noise or environmental coupling can probe the transition from quantum-like to classical behavior.

---

## Relation to Foundational Quantum Mechanics Literature

### Dirac, Feynman, Bohm, and the Copenhagen Interpretation

- **Dirac (1930)**: Formalized the principle of superposition and the operator-based framework of QM, emphasizing the mathematical structure over physical interpretation.
- **Feynman (1965)**: Introduced the path integral formulation, interpreting quantum amplitudes as sums over all possible paths, with interference arising from phase differences.
- **Bohm (1952)**: Developed a deterministic, trajectory-based interpretation (Bohmian mechanics), with particles guided by a quantum potential derived from the wavefunction.
- **Copenhagen Interpretation**: Emphasizes the fundamental role of measurement, probabilistic collapse, and the limits of classical description.

The CA model aligns with the **deterministic aspirations** of Bohmian mechanics and 't Hooft's CA interpretation, while seeking to reproduce the statistical predictions of standard QM via deterministic, tick-frame-based dynamics.

### Recent Developments in CA and Deterministic Models

- **Cellular Automaton Interpretation**: 't Hooft (2016) and others have argued for a deterministic, CA-based underpinning to quantum phenomena, with quantum states emerging as statistical descriptions of underlying CA dynamics.
- **Deterministic Dynamical Systems**: Recent work (Rahman 2024; Tsai & Hong 2025; Declercq 2025) has demonstrated that deterministic, locally interacting systems can reproduce quantum-like interference and tunneling phenomena at the ensemble level.
- **Collapse Models**: Objective collapse theories (GRW, CSL, collapse points) introduce stochastic or deterministic modifications to the Schrödinger equation to account for measurement-induced localization, some of which can be mapped onto CA-like dynamics.

---

## Tables and Diagrams

### Table 1: Comparison of Standard QM and CA-Based Deterministic Model

| Feature                       | Standard QM                        | CA-Based Deterministic Model              |
|-------------------------------|------------------------------------|-------------------------------------------|
| State Representation          | Complex wavefunction \( \psi(r, t) \) | Distributed brok cloud in CA substrate    |
| Time Evolution                | Unitary, linear (Schrödinger eq.)  | Deterministic, tick-frame CA updates      |
| Superposition                 | Fundamental principle              | Emergent from distributed brok dynamics   |
| Measurement                   | Probabilistic collapse (Born rule) | Deterministic collapse via gamma impulse  |
| Interference                  | Wavefunction superposition         | Sensitive brok trajectory evolution       |
| Decoherence                   | Environment-induced, stochastic    | CA substrate/environment coupling         |
| Nonlocality                   | Intrinsic (entanglement, Bell)     | Possible via CA/global field structure    |
| Falsifiability                | Well-tested, but interpretational issues | Predicts deviations under controlled conditions |

**Analysis**: This table highlights the core similarities and differences between the standard quantum mechanical framework and the deterministic CA-based model. While both can reproduce the observed interference patterns and measurement statistics under appropriate conditions, the underlying ontologies and mechanisms differ fundamentally.

---

## Discussion

### Strengths and Novel Predictions

The deterministic, tick-frame-based CA model offers a **realist, mechanistic account** of the double-slit experiment, eschewing the need for intrinsic randomness or nonlocal collapse. By modeling the electron as a distributed brok cloud and measurement as a deterministic gamma-induced collapse, the framework provides a concrete substrate for exploring the emergence of quantum-like phenomena from underlying deterministic dynamics.

**Novel Predictions**:
- **Pattern Sensitivity**: The interference pattern's detailed structure depends sensitively on the slit geometry, gamma field profile, and CA substrate properties, potentially enabling experimental tests that distinguish the model from standard QM.
- **Deviations from Born Rule**: Under controlled initial conditions or substrate modifications, the model may predict deviations from the Born rule, providing a falsifiable signature.
- **Decoherence Mechanisms**: The explicit modeling of environment coupling in the CA substrate offers new insights into the transition from quantum to classical behavior.

### Limitations and Open Questions

- **Universality**: Can the CA model reproduce all quantum phenomena, including entanglement, contextuality, and Bell inequality violations?
- **Parameter Tuning**: How robust are the model's predictions to variations in CA rules, gamma field structure, and initial conditions?
- **Physical Realization**: Is there a plausible mapping from the CA substrate and brok dynamics to physical systems, or is the model purely computational?

### Relation to Other Interpretations

The CA model bridges the gap between **Bohmian mechanics**, **objective collapse theories**, and **CA interpretations** of quantum mechanics, offering a unified framework for exploring deterministic underpinnings of quantum phenomena. Its explicit tick-frame dynamics and distributed structure provide a fertile ground for further theoretical and experimental investigation.

---

## Conclusion

This report has presented a comprehensive, formal experimental framework for a deterministic, tick-frame-based reinterpretation of the double-slit experiment, grounded in a cellular automaton substrate and structured gamma field dynamics. By modeling the electron as a distributed brok cloud and measurement as a deterministic gamma-induced collapse, the framework reproduces the key features of quantum interference and measurement-induced localization, while offering novel predictions and avenues for experimental falsification.

The model stands as a compelling alternative to standard quantum mechanics, Bohmian mechanics, and other deterministic interpretations, providing a concrete substrate for exploring the emergence of quantum phenomena from underlying deterministic dynamics. Future work will focus on extending the model to multi-particle systems, entanglement, and the exploration of its experimental signatures in controlled settings.

---

**Key References Cited Inline**:

- Dirac, P. A. M. (1930). *The Principles of Quantum Mechanics*
- Feynman, R. P., Leighton, R. B., & Sands, M. L. (1965). *The Feynman Lectures on Physics*
- Bohm, D. (1952). *A Suggested Interpretation of the Quantum Theory in Terms of "Hidden" Variables*
- 't Hooft, G. (2016). *The Cellular Automaton Interpretation of Quantum Mechanics*
- Tsai, P.-R., & Hong, T.-M. (2025). *A Dough-Like Model for Understanding Double-Slit Phenomena*
- Rahman, A. (2024). *Towards a Deterministic Interpretation of Quantum Mechanics: Insights from Dynamical Systems*
- Declercq, N. F. (2025). *Beyond Superposition and Collapse: Double-Slit Interference from Trembling Spacetime Geodesics*
- Chertock, A. (2021). *A Practical Guide to Deterministic Particle Methods*
- Adamatzky, A., & Chua, L. (2011). *Memristive Excitable Cellular Automata*
- Farrelly, T. (2020). *A Review of Quantum Cellular Automata*

---
