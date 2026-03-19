# Minimal Model Recommendation for Time–Visualization Testing

## 1. Goals

- Provide a **continuous root evolution** to preserve relativity compatibility.
- Implement **discrete commits** via PoF thresholding to exercise tick rules.
- Generate **observable artefacts** to embed “past” into the present tick.
- Keep parameters minimal for easy tuning, auditing, and falsification.

---

## 2. Core Minimal Model

### Root Substrate

- **State:** \(x(t)\in\mathbb{R}^{d}\) with small dimension (e.g., \(d=2\) or \(4\)).
- **Dynamics:**  
  \[
  \dot{x}(t)=A x(t)+b
  \]
  where \(A\) is stable (negative real eigenvalues).
- **Reason:** Linear flow ensures analytic solutions and controlled complexity.

### Tick Generator and PoF

- **Clock:**  
  \[
  \dot{\Theta}(t)=\omega_P\,F(x(t))
  \]
- **Commit rule:**  
  \[
  \Theta(t^-)\!<\!n+\delta \land \Theta(t)\!\ge\!n+\delta \Rightarrow \text{emit PoF at }t_n
  \]
- **Hysteresis:** \(\delta>0\) prevents chattering.
- **Reason:** Directly tests temporal rules and stability guards.

### Artefact Field (Seeing the Past)

- **Carrier equation (scalar wave):**  
  \[
  \partial_{tt}\mathcal{A}-c^2\nabla^2 \mathcal{A}+\gamma\,\partial_t\mathcal{A}=J(x,t)
  \]
- **Emission:**  
  \[
  J(x,t)=\sum_{n} q_n\,\delta(t-t_n)\,\delta(x-x_n)
  \]
  with \(q_n=\alpha_0+\alpha_1\|x(t_n)\|\).
- **Reason:** Wave equation provides causal propagation; artefacts are easy to tag and observe.

### Agent Refresh and Observation

- **Subset refresh:**  
  \[
  r_a(t)=\frac{1}{M}\,\omega_P F(x(t)),\quad M\in\mathbb{N}^+
  \]
- **Accumulator:**  
  \[
  \dot{\Psi}(t)=r_a(t)\,S(\mathcal{A}(\cdot,t),a)
  \]
  Commit when \(\Psi\ge 1+\varepsilon\).
- **Salience functional:**  
  \[
  S=\int w(x)\,\mathcal{A}(x,t)^2\,dx
  \]
- **Reason:** Minimal percept loop to validate synchronization and embedded memory reading.

---

## 3. Modulation Choices for \(F(x)\)

- **Constant baseline:** \(F(x)\equiv 1\) → pure Planck ticks.
- **Energy-coupled:**  
  \[
  F(x)=\text{clip}(a_0+a_1\|x\|,\ \epsilon,\ F_{\max})
  \]
- **Velocity proxy (optional):**  
  \[
  F(x,v)=F_0(x)\,\sqrt{1-\frac{v^2}{c^2}}
  \]
- **Curvature proxy (optional):**  
  \[
  F(x)=F_0(x)\,(1+\beta\,\|x\|)
  \]

---

## 4. Starter Configuration and Outputs

### Parameters

- Linear flow:  
  \[
  A=\begin{bmatrix}-\lambda & 0\\ 0 & -\lambda\end{bmatrix},\quad b=0,\quad \lambda>0
  \]
- Clock: \(\omega_P=1/t_P,\ F(x)\equiv 1,\ \delta=0.1\).
- Wave: 1D lattice, \(c=1,\ \gamma=0.01\).
- Emission: \(x_n=x(t_n),\ q_n=\alpha_0+\alpha_1\|x_n\|\).

### Logged Outputs

- **Root commits:** \((n, t_n, \Theta(t_n), x(t_n), F(x_n), \text{Mode}=\text{COMMIT})\).
- **Artefacts:** \((n, q_n, x_n, \text{Tag}_n)\) and \(\mathcal{A}(x,t_n)\) snapshots.
- **Agent frames:** \((k, t_k, \Psi(t_k), S, M, \text{Mode})\).

---

## 5. Why This Is the Simplest That Works

- **Few moving parts:** Linear ODE + scalar wave + thresholding.
- **Direct tests:** Time commits, embedded memory, agent synchronization.
- **Extensible knobs:** Swap \(F(x)\) from constant to energy/velocity/curvature to reproduce dilation effects.
- **Audit-ready:** Every event taggable; chattering and ordering handled via hysteresis and merge policy.

---

## 6. Next Step

Convert this specification into a **pseudo‑code simulation** with discrete time‑stepping and test cases:

- Baseline (constant \(F(x)\)).
- High‑energy modulation.
- Boosted observer (velocity proxy).
- High‑density proxy (curvature).

This validates the full time–visualization pipeline.
