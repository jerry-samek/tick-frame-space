"""
Validate tick-frame physics theory predictions against experimental salience data.

Theory: Damped wave equation in discrete space-time
psi_next = 2*psi - psi_prev + nabla^2*psi - gamma*(psi - psi_prev)

Predictions:
1. Wave amplitude scaling: ~ 1/r^(d-1)
2. Salience scaling: ~ r^(2-d) from volume integration
3. Multi-source interference: N^2 for constructive
4. Damping effects: exponential decay e^(-gamma*t)
5. Time evolution: approach to steady state
6. 2D critical behavior
7. alpha_0 threshold: salience ~ alpha_0^2
8. High-D geometry independence
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import seaborn as sns
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load all data
print("Loading data...")
data_1d = pd.read_csv('v6_gpu_1d_results.csv')
data_2d = pd.read_csv('v6_gpu_2d_results.csv')
data_3d = pd.read_csv('v6_gpu_3d_results.csv')
data_4d = pd.read_csv('v6_gpu_4d_results.csv')
data_5d = pd.read_csv('v6_gpu_5d_results.csv')

# Add dimension column to each
data_1d['dimension'] = 1
data_2d['dimension'] = 2
data_3d['dimension'] = 3
data_4d['dimension'] = 4
data_5d['dimension'] = 5

# Combine all data
all_data = pd.concat([data_1d, data_2d, data_3d, data_4d, data_5d], ignore_index=True)

print(f"Total experiments: {len(all_data)}")
print(f"\nData columns: {all_data.columns.tolist()}")
print(f"\nData shape by dimension:")
for d in [1, 2, 3, 4, 5]:
    print(f"  {d}D: {len(all_data[all_data['dimension'] == d])} experiments")

# Create output storage
validation_results = {}
fitted_parameters = {}

# ============================================================================
# 1. DIMENSIONAL SCALING ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("1. DIMENSIONAL SCALING ANALYSIS")
print("="*80)

# Theoretical prediction: salience ~ r^(2-d)
# For point source at distance, but we measure max_salience
# Expected: strong decay with dimension

# Group by dimension, compute statistics
dim_stats = all_data.groupby('dimension').agg({
    'max_salience': ['mean', 'std', 'median', 'max'],
    'has_commits': 'mean',
    'commit_rate': 'mean'
}).reset_index()

print("\nDimensional statistics (max_salience):")
print(dim_stats)

# Fit power law: salience(d) ~ d^β
dimensions = np.array([1, 2, 3, 4, 5])
mean_salience = all_data.groupby('dimension')['max_salience'].mean().values
max_salience_by_dim = all_data.groupby('dimension')['max_salience'].max().values

def power_law(d, A, beta):
    return A * d**beta

def exponential_decay(d, A, lam):
    return A * np.exp(-lam * d)

# Fit both models
try:
    # Power law fit
    popt_power, pcov_power = curve_fit(power_law, dimensions, mean_salience,
                                        p0=[1.0, -1.0], maxfev=10000)
    A_power, beta_power = popt_power
    pred_power = power_law(dimensions, A_power, beta_power)
    r2_power = 1 - np.sum((mean_salience - pred_power)**2) / np.sum((mean_salience - mean_salience.mean())**2)

    # Exponential fit
    popt_exp, pcov_exp = curve_fit(exponential_decay, dimensions, mean_salience,
                                   p0=[1.0, 0.5], maxfev=10000)
    A_exp, lam_exp = popt_exp
    pred_exp = exponential_decay(dimensions, A_exp, lam_exp)
    r2_exp = 1 - np.sum((mean_salience - pred_exp)**2) / np.sum((mean_salience - mean_salience.mean())**2)

    print(f"\nPower law fit: salience(d) = {A_power:.6f} * d^{beta_power:.3f}")
    print(f"  R² = {r2_power:.4f}")
    print(f"\nExponential fit: salience(d) = {A_exp:.6f} * exp(-{lam_exp:.3f} * d)")
    print(f"  R² = {r2_exp:.4f}")

    # Theoretical prediction: salience ~ r^(2-d)
    # For fixed geometry, this translates to exponential-like decay
    print(f"\nTheoretical expectation: r^(2-d) → exponential decay with d")
    print(f"Observed decay rate λ = {lam_exp:.3f}")

    validation_results['dimensional_scaling'] = {
        'power_law_exponent': beta_power,
        'power_law_R2': r2_power,
        'exp_decay_rate': lam_exp,
        'exp_R2': r2_exp,
        'best_fit': 'exponential' if r2_exp > r2_power else 'power_law'
    }

    fitted_parameters['dimensional_scaling'] = {
        'dimensions': dimensions.tolist(),
        'mean_salience': mean_salience.tolist(),
        'power_law_fit': pred_power.tolist(),
        'exponential_fit': pred_exp.tolist()
    }

except Exception as e:
    print(f"Error in dimensional scaling fit: {e}")

# ============================================================================
# 2. SOURCE SCALING VALIDATION (Ms dependence)
# ============================================================================
print("\n" + "="*80)
print("2. SOURCE SCALING VALIDATION")
print("="*80)

# Theory: N sources with constructive interference → N² amplitude
# Salience ~ amplitude² → salience ~ N^4 for perfect constructive
# But with phases, expect partial cancellation

source_scaling = {}

for dim in [1, 2, 3, 4, 5]:
    dim_data = all_data[all_data['dimension'] == dim]

    # Group by num_sources (Ms)
    if 'num_sources' in dim_data.columns:
        source_stats = dim_data.groupby('num_sources').agg({
            'max_salience': ['mean', 'std', 'count']
        }).reset_index()

        if len(source_stats) > 2:
            Ms = source_stats['num_sources'].values
            sal_mean = source_stats['max_salience']['mean'].values

            # Fit: salience ~ Ms^ρ
            try:
                log_Ms = np.log(Ms)
                log_sal = np.log(sal_mean + 1e-10)  # Avoid log(0)

                coeffs = np.polyfit(log_Ms, log_sal, 1)
                rho = coeffs[0]
                log_A = coeffs[1]

                pred_log_sal = np.polyval(coeffs, log_Ms)
                r2 = 1 - np.sum((log_sal - pred_log_sal)**2) / np.sum((log_sal - log_sal.mean())**2)

                print(f"\n{dim}D: salience ~ Ms^{rho:.3f}, R² = {r2:.4f}")
                print(f"  Theory: ρ = 2 for constructive, ρ → 0 for destructive")

                source_scaling[dim] = {
                    'exponent': rho,
                    'R2': r2,
                    'Ms_values': Ms.tolist(),
                    'salience_values': sal_mean.tolist()
                }

            except Exception as e:
                print(f"\n{dim}D: Error fitting source scaling: {e}")

validation_results['source_scaling'] = source_scaling
fitted_parameters['source_scaling'] = source_scaling

# ============================================================================
# 3. DAMPING VALIDATION (γ comparison)
# ============================================================================
print("\n" + "="*80)
print("3. DAMPING VALIDATION")
print("="*80)

# Theory: salience ~ 1/γ (inverse proportional)
# Expected ratio: salience(γ=0.001) / salience(γ=0.005) ≈ 5

damping_validation = {}

for dim in [1, 2, 3, 4, 5]:
    dim_data = all_data[all_data['dimension'] == dim]

    # Separate by gamma
    gamma_001 = dim_data[dim_data['gamma'] == 0.001]['max_salience'].mean()
    gamma_005 = dim_data[dim_data['gamma'] == 0.005]['max_salience'].mean()

    if gamma_001 > 0 and gamma_005 > 0:
        ratio_observed = gamma_001 / gamma_005
        ratio_expected = 0.005 / 0.001  # = 5

        print(f"\n{dim}D: γ=0.001 / γ=0.005 = {ratio_observed:.3f} (expected: {ratio_expected:.1f})")
        print(f"  Agreement: {ratio_observed/ratio_expected*100:.1f}%")

        damping_validation[dim] = {
            'gamma_001_salience': gamma_001,
            'gamma_005_salience': gamma_005,
            'ratio_observed': ratio_observed,
            'ratio_expected': ratio_expected,
            'agreement_pct': ratio_observed/ratio_expected*100
        }

validation_results['damping_validation'] = damping_validation

# ============================================================================
# 4. TIME EVOLUTION TO STEADY STATE
# ============================================================================
print("\n" + "="*80)
print("4. TIME EVOLUTION ANALYSIS")
print("="*80)

# Theory: salience(T) = A(1 - e^(-T/τ)) where τ ~ 1/γ
# For γ = 0.001, τ_expected ~ 1000
# For γ = 0.005, τ_expected ~ 200

time_evolution = {}

for dim in [1, 2, 3, 4, 5]:
    for gamma in [0.001, 0.005]:
        dim_gamma_data = all_data[(all_data['dimension'] == dim) &
                                   (all_data['gamma'] == gamma)]

        # Group by T
        time_stats = dim_gamma_data.groupby('T').agg({
            'max_salience': ['mean', 'std']
        }).reset_index()

        if len(time_stats) > 2:
            T = time_stats['T'].values
            sal = time_stats['max_salience']['mean'].values

            # Fit exponential approach
            def steady_state(t, A, tau):
                return A * (1 - np.exp(-t/tau))

            try:
                # Initial guess: A = max salience, τ = 1/γ
                p0 = [sal.max() * 1.2, 1/gamma]
                popt, _ = curve_fit(steady_state, T, sal, p0=p0, maxfev=10000)
                A_fit, tau_fit = popt

                pred_sal = steady_state(T, A_fit, tau_fit)
                r2 = 1 - np.sum((sal - pred_sal)**2) / np.sum((sal - sal.mean())**2)

                tau_expected = 1/gamma

                print(f"\n{dim}D, γ={gamma}: τ = {tau_fit:.1f} (expected: {tau_expected:.1f}), R² = {r2:.4f}")

                key = f"{dim}D_gamma{gamma}"
                time_evolution[key] = {
                    'tau_fit': tau_fit,
                    'tau_expected': tau_expected,
                    'A_fit': A_fit,
                    'R2': r2,
                    'T_values': T.tolist(),
                    'salience_values': sal.tolist()
                }

            except Exception as e:
                print(f"\n{dim}D, γ={gamma}: Error fitting time evolution: {e}")

validation_results['time_evolution'] = time_evolution
fitted_parameters['time_evolution'] = time_evolution

# ============================================================================
# 5. α₀ THRESHOLD ESTIMATION
# ============================================================================
print("\n" + "="*80)
print("5. α₀ THRESHOLD ANALYSIS")
print("="*80)

# Theory: salience ~ α₀²
# Threshold α₀_c where salience ≈ 1

alpha_validation = {}

for dim in [1, 2, 3, 4, 5]:
    dim_data = all_data[all_data['dimension'] == dim]

    # Group by α₀
    alpha_stats = dim_data.groupby('alpha_0').agg({
        'max_salience': ['mean', 'std'],
        'has_commits': 'mean'
    }).reset_index()

    if len(alpha_stats) > 2:
        alpha = alpha_stats['alpha_0'].values
        sal = alpha_stats['max_salience']['mean'].values

        # Fit quadratic: salience = A * α₀²
        try:
            # Log-log fit
            log_alpha = np.log(alpha)
            log_sal = np.log(sal + 1e-10)

            coeffs = np.polyfit(log_alpha, log_sal, 1)
            exponent = coeffs[0]
            log_A = coeffs[1]

            pred_log_sal = np.polyval(coeffs, log_alpha)
            r2 = 1 - np.sum((log_sal - pred_log_sal)**2) / np.sum((log_sal - log_sal.mean())**2)

            print(f"\n{dim}D: salience ~ α₀^{exponent:.3f}, R² = {r2:.4f}")
            print(f"  Theory: exponent = 2 (quadratic)")

            # Estimate threshold: where salience = 1
            A = np.exp(log_A)
            alpha_threshold = (1.0 / A)**(1/exponent)

            print(f"  Estimated α₀ threshold: {alpha_threshold:.3f}")

            alpha_validation[dim] = {
                'exponent': exponent,
                'R2': r2,
                'threshold_estimate': alpha_threshold,
                'alpha_values': alpha.tolist(),
                'salience_values': sal.tolist()
            }

        except Exception as e:
            print(f"\n{dim}D: Error fitting α₀ scaling: {e}")

validation_results['alpha_validation'] = alpha_validation
fitted_parameters['alpha_validation'] = alpha_validation

# ============================================================================
# 6. 2D CRITICAL BEHAVIOR
# ============================================================================
print("\n" + "="*80)
print("6. 2D CRITICAL BEHAVIOR ANALYSIS")
print("="*80)

# Theory: d=2 is critical dimension for wave equation
# Expect logarithmic divergence, special behavior

# Compare 1D, 2D, 3D more carefully
print("\nComparing low dimensions:")
for dim in [1, 2, 3]:
    dim_data = all_data[all_data['dimension'] == dim]
    mean_sal = dim_data['max_salience'].mean()
    max_sal = dim_data['max_salience'].max()
    std_sal = dim_data['max_salience'].std()

    print(f"{dim}D: mean={mean_sal:.6f}, max={max_sal:.6f}, std={std_sal:.6f}")

# Check if 2D has special scaling
dim2_data = all_data[all_data['dimension'] == 2]

# Look at spatial scaling in 2D
# For 2D: salience ~ ln(r) theoretically
print("\n2D analysis:")
print(f"  Number of experiments: {len(dim2_data)}")
print(f"  Mean salience: {dim2_data['max_salience'].mean():.6f}")
print(f"  Salience range: [{dim2_data['max_salience'].min():.6f}, {dim2_data['max_salience'].max():.6f}]")

validation_results['2d_critical'] = {
    'mean_salience': dim2_data['max_salience'].mean(),
    'is_anomalous': dim2_data['max_salience'].mean() > all_data.groupby('dimension')['max_salience'].mean().mean()
}

# ============================================================================
# 7. GEOMETRY AND PHASE INDEPENDENCE
# ============================================================================
print("\n" + "="*80)
print("7. GEOMETRY AND PHASE INDEPENDENCE")
print("="*80)

# Theory: In high dimensions, configuration becomes irrelevant
# Check if geometry/phase effects vanish with dimension

geometry_effects = {}

for dim in [1, 2, 3, 4, 5]:
    dim_data = all_data[all_data['dimension'] == dim]

    if 'geometry' in dim_data.columns:
        # Compare geometries
        geom_stats = dim_data.groupby('geometry')['max_salience'].agg(['mean', 'std', 'count'])

        if len(geom_stats) > 1:
            variance_ratio = geom_stats['std'].max() / (geom_stats['mean'].mean() + 1e-10)

            print(f"\n{dim}D geometry variation:")
            print(geom_stats)
            print(f"  Coefficient of variation: {variance_ratio:.4f}")

            geometry_effects[dim] = {
                'cv': variance_ratio,
                'geometries': geom_stats.to_dict()
            }

validation_results['geometry_independence'] = geometry_effects

# Check phase independence
phase_effects = {}

for dim in [1, 2, 3, 4, 5]:
    dim_data = all_data[all_data['dimension'] == dim]

    if 'phase_offset' in dim_data.columns:
        # Compare phases
        phase_stats = dim_data.groupby('phase_offset')['max_salience'].agg(['mean', 'std', 'count'])

        if len(phase_stats) > 1:
            variance_ratio = phase_stats['std'].max() / (phase_stats['mean'].mean() + 1e-10)

            print(f"\n{dim}D phase variation:")
            print(phase_stats)
            print(f"  Coefficient of variation: {variance_ratio:.4f}")

            phase_effects[dim] = {
                'cv': variance_ratio,
                'phases': phase_stats.to_dict()
            }

validation_results['phase_independence'] = phase_effects

# ============================================================================
# 8. RESIDUAL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("8. RESIDUAL ANALYSIS")
print("="*80)

# Combine all predictions and compute residuals
# For each dimension, compare observed vs predicted salience

residuals_summary = {}

# Use exponential model for dimensional prediction
if 'dimensional_scaling' in validation_results:
    A_exp = A_exp if 'A_exp' in locals() else 1.0
    lam_exp = lam_exp if 'lam_exp' in locals() else 0.5

    for dim in [1, 2, 3, 4, 5]:
        observed = all_data[all_data['dimension'] == dim]['max_salience'].mean()
        predicted = A_exp * np.exp(-lam_exp * dim)
        residual = observed - predicted
        relative_error = abs(residual) / (observed + 1e-10) * 100

        print(f"{dim}D: observed={observed:.6f}, predicted={predicted:.6f}, error={relative_error:.1f}%")

        residuals_summary[dim] = {
            'observed': observed,
            'predicted': predicted,
            'residual': residual,
            'relative_error_pct': relative_error
        }

validation_results['residuals'] = residuals_summary

# ============================================================================
# 9. SAVE FITTED PARAMETERS
# ============================================================================
print("\n" + "="*80)
print("9. SAVING RESULTS")
print("="*80)

# Save fitted parameters to CSV
fit_data = []

# Dimensional scaling
if 'dimensional_scaling' in validation_results:
    ds = validation_results['dimensional_scaling']
    for i, dim in enumerate(dimensions):
        fit_data.append({
            'analysis': 'dimensional_scaling',
            'dimension': dim,
            'parameter': 'power_law_exponent',
            'value': ds['power_law_exponent'],
            'R2': ds['power_law_R2']
        })

# Source scaling exponents
for dim, params in source_scaling.items():
    fit_data.append({
        'analysis': 'source_scaling',
        'dimension': dim,
        'parameter': 'exponent_rho',
        'value': params['exponent'],
        'R2': params['R2']
    })

# Damping ratios
for dim, params in damping_validation.items():
    fit_data.append({
        'analysis': 'damping',
        'dimension': dim,
        'parameter': 'ratio_observed',
        'value': params['ratio_observed'],
        'R2': params['agreement_pct'] / 100
    })

# Alpha exponents
for dim, params in alpha_validation.items():
    fit_data.append({
        'analysis': 'alpha_threshold',
        'dimension': dim,
        'parameter': 'exponent',
        'value': params['exponent'],
        'R2': params['R2']
    })
    fit_data.append({
        'analysis': 'alpha_threshold',
        'dimension': dim,
        'parameter': 'threshold',
        'value': params['threshold_estimate'],
        'R2': params['R2']
    })

fit_df = pd.DataFrame(fit_data)
fit_df.to_csv('salience_theory_fits.csv', index=False)
print("Saved: salience_theory_fits.csv")

# ============================================================================
# 10. CREATE COMPREHENSIVE VISUALIZATION
# ============================================================================
print("\n" + "="*80)
print("10. CREATING VISUALIZATION")
print("="*80)

fig = plt.figure(figsize=(20, 24))
gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.25)

# Panel 1: Dimensional scaling
ax1 = fig.add_subplot(gs[0, 0])
ax1.semilogy(dimensions, mean_salience, 'o-', markersize=10, linewidth=2, label='Observed (mean)')
if 'dimensional_scaling' in validation_results:
    ax1.semilogy(dimensions, pred_exp, '--', linewidth=2, label=f'Exponential fit (λ={lam_exp:.3f})')
    ax1.semilogy(dimensions, pred_power, ':', linewidth=2, label=f'Power law (β={beta_power:.3f})')
ax1.set_xlabel('Dimension d', fontsize=12)
ax1.set_ylabel('Mean Salience', fontsize=12)
ax1.set_title('Panel 1: Dimensional Scaling\nTheory: salience ~ r^(2-d)', fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel 2: Source scaling for each dimension
ax2 = fig.add_subplot(gs[0, 1])
colors = plt.cm.viridis(np.linspace(0, 1, 5))
for i, dim in enumerate([1, 2, 3, 4, 5]):
    if dim in source_scaling:
        Ms = np.array(source_scaling[dim]['Ms_values'])
        sal = np.array(source_scaling[dim]['salience_values'])
        rho = source_scaling[dim]['exponent']
        ax2.loglog(Ms, sal, 'o-', color=colors[i], label=f'{dim}D (ρ={rho:.2f})', markersize=6)
ax2.set_xlabel('Number of Sources (Ms)', fontsize=12)
ax2.set_ylabel('Mean Salience', fontsize=12)
ax2.set_title('Panel 2: Source Scaling\nTheory: salience ~ Ms^ρ (ρ=2 constructive)', fontsize=13, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Panel 3: Damping ratio validation
ax3 = fig.add_subplot(gs[1, 0])
dims_damping = list(damping_validation.keys())
ratios_obs = [damping_validation[d]['ratio_observed'] for d in dims_damping]
ratios_exp = [damping_validation[d]['ratio_expected'] for d in dims_damping]
x = np.arange(len(dims_damping))
width = 0.35
ax3.bar(x - width/2, ratios_obs, width, label='Observed', alpha=0.8)
ax3.bar(x + width/2, ratios_exp, width, label='Expected (5×)', alpha=0.8)
ax3.set_xlabel('Dimension', fontsize=12)
ax3.set_ylabel('Salience Ratio (γ=0.001 / γ=0.005)', fontsize=12)
ax3.set_title('Panel 3: Damping Validation\nTheory: ratio = γ₂/γ₁ = 5', fontsize=13, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels([f'{d}D' for d in dims_damping])
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Panel 4: Time evolution (show 3D, γ=0.001 as example)
ax4 = fig.add_subplot(gs[1, 1])
example_dim = 3
example_gamma = 0.001
key = f"{example_dim}D_gamma{example_gamma}"
if key in time_evolution:
    T = np.array(time_evolution[key]['T_values'])
    sal = np.array(time_evolution[key]['salience_values'])
    tau = time_evolution[key]['tau_fit']
    A = time_evolution[key]['A_fit']

    ax4.plot(T, sal, 'o', markersize=8, label='Observed')
    T_smooth = np.linspace(T.min(), T.max(), 100)
    sal_smooth = A * (1 - np.exp(-T_smooth/tau))
    ax4.plot(T_smooth, sal_smooth, '--', linewidth=2, label=f'Fit: τ={tau:.1f}')
    ax4.axhline(A, color='red', linestyle=':', alpha=0.5, label=f'Asymptote: A={A:.4f}')
ax4.set_xlabel('Time Horizon T', fontsize=12)
ax4.set_ylabel('Mean Salience', fontsize=12)
ax4.set_title(f'Panel 4: Time Evolution ({example_dim}D, γ={example_gamma})\nTheory: τ ~ 1/γ', fontsize=13, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Panel 5: α₀ threshold correlation
ax5 = fig.add_subplot(gs[2, 0])
for i, dim in enumerate([1, 2, 3, 4, 5]):
    if dim in alpha_validation:
        alpha = np.array(alpha_validation[dim]['alpha_values'])
        sal = np.array(alpha_validation[dim]['salience_values'])
        exp = alpha_validation[dim]['exponent']
        ax5.loglog(alpha, sal, 'o-', color=colors[i], label=f'{dim}D (exp={exp:.2f})', markersize=6)
ax5.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='Threshold')
ax5.set_xlabel('Source Strength α₀', fontsize=12)
ax5.set_ylabel('Mean Salience', fontsize=12)
ax5.set_title('Panel 5: α₀ Threshold Scaling\nTheory: salience ~ α₀² ', fontsize=13, fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Panel 6: 2D critical behavior (detailed comparison)
ax6 = fig.add_subplot(gs[2, 1])
for dim in [1, 2, 3]:
    dim_data = all_data[all_data['dimension'] == dim]
    salience_dist = dim_data['max_salience']
    ax6.hist(salience_dist, bins=30, alpha=0.5, label=f'{dim}D', density=True)
ax6.set_xlabel('Max Salience', fontsize=12)
ax6.set_ylabel('Density', fontsize=12)
ax6.set_title('Panel 6: 2D Critical Behavior\nComparing salience distributions', fontsize=13, fontweight='bold')
ax6.legend()
ax6.grid(True, alpha=0.3)

# Panel 7: Phase space heatmap (dimension × α₀)
ax7 = fig.add_subplot(gs[3, 0])
# Create pivot table
pivot_data = all_data.pivot_table(values='max_salience', index='alpha_0', columns='dimension', aggfunc='mean')
im = ax7.imshow(pivot_data.values, aspect='auto', cmap='viridis', origin='lower')
ax7.set_xticks(range(len(pivot_data.columns)))
ax7.set_xticklabels([f'{d}D' for d in pivot_data.columns])
ax7.set_yticks(range(0, len(pivot_data.index), max(1, len(pivot_data.index)//10)))
ax7.set_yticklabels([f'{pivot_data.index[i]:.1f}' for i in range(0, len(pivot_data.index), max(1, len(pivot_data.index)//10))])
ax7.set_xlabel('Dimension', fontsize=12)
ax7.set_ylabel('α₀', fontsize=12)
ax7.set_title('Panel 7: Phase Space (dimension × α₀)', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax7, label='Mean Salience')

# Panel 8: Residuals analysis
ax8 = fig.add_subplot(gs[3, 1])
if residuals_summary:
    dims_res = list(residuals_summary.keys())
    residuals = [residuals_summary[d]['residual'] for d in dims_res]
    rel_errors = [residuals_summary[d]['relative_error_pct'] for d in dims_res]

    ax8_twin = ax8.twinx()
    line1 = ax8.plot(dims_res, residuals, 'o-', color='blue', markersize=10, linewidth=2, label='Residual')
    line2 = ax8_twin.plot(dims_res, rel_errors, 's--', color='red', markersize=8, linewidth=2, label='Relative Error %')
    ax8.axhline(0, color='black', linestyle='-', alpha=0.3)
    ax8.set_xlabel('Dimension', fontsize=12)
    ax8.set_ylabel('Residual (observed - predicted)', fontsize=12, color='blue')
    ax8_twin.set_ylabel('Relative Error (%)', fontsize=12, color='red')
    ax8.set_title('Panel 8: Residual Analysis', fontsize=13, fontweight='bold')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax8.legend(lines, labels, loc='upper left')
    ax8.grid(True, alpha=0.3)

plt.suptitle('TICK-FRAME PHYSICS THEORY VALIDATION\nDamped Wave Equation in Discrete Space-Time',
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('theoretical_validation.png', dpi=300, bbox_inches='tight')
print("Saved: theoretical_validation.png")
plt.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nGenerated files:")
print("  1. salience_theory_fits.csv")
print("  2. theoretical_validation.png")
print("\nValidation results stored in memory for report generation.")
