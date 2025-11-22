"""
Visualize V3 results: Ultra-fine threshold and dynamic buildup analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Load data
print("Loading data...")
df_ultra = pd.read_csv("ultra_fine_results.csv")

with open("dynamic_buildup_results.json", 'r') as f:
    dynamic_data = json.load(f)

# Create comprehensive figure
fig = plt.figure(figsize=(18, 12))

# ========================================
# Plot 1: Ultra-fine threshold (gamma=0.001)
# ========================================
ax1 = plt.subplot(3, 3, 1)
subset = df_ultra[df_ultra['gamma'] == 0.001]
subset = subset.sort_values('alpha_0')

ax1.plot(subset['alpha_0'], subset['has_commits'].astype(int),
         marker='o', linewidth=3, markersize=8, color='darkblue')
ax1.set_xlabel('alpha_0', fontsize=11)
ax1.set_ylabel('Has Commits (0/1)', fontsize=11)
ax1.set_title('Ultra-Fine Onset (gamma=0.001, M=1)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.1, 1.1)

# ========================================
# Plot 2: Final Psi vs alpha_0 (ultra-fine)
# ========================================
ax2 = plt.subplot(3, 3, 2)
subset = df_ultra[df_ultra['gamma'] == 0.001]
subset = subset.sort_values('alpha_0')

ax2.plot(subset['alpha_0'], subset['final_psi'],
         marker='o', linewidth=3, markersize=8, color='purple')
ax2.axhline(y=1.01, color='red', linestyle='--', linewidth=2, label='Threshold')
ax2.set_xlabel('alpha_0', fontsize=11)
ax2.set_ylabel('Final Psi', fontsize=11)
ax2.set_title('Salience Accumulation (ultra-fine)', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Annotate threshold crossing
threshold_idx = subset[subset['has_commits'] == True].index[0] if len(subset[subset['has_commits'] == True]) > 0 else None
if threshold_idx is not None:
    threshold_alpha = subset.loc[threshold_idx, 'alpha_0']
    threshold_psi = subset.loc[threshold_idx, 'final_psi']
    ax2.annotate(f'Onset\nat {threshold_alpha:.2f}',
                xy=(threshold_alpha, threshold_psi),
                xytext=(threshold_alpha-0.05, threshold_psi+0.2),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, color='red', fontweight='bold')

# ========================================
# Plot 3: Delta Psi (distance to threshold)
# ========================================
ax3 = plt.subplot(3, 3, 3)
subset = df_ultra[df_ultra['gamma'] == 0.001]
subset = subset.sort_values('alpha_0')

colors = ['red' if x < 0 else 'green' for x in subset['delta_psi']]
ax3.bar(subset['alpha_0'], subset['delta_psi'], width=0.008, color=colors, alpha=0.7)
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax3.set_xlabel('alpha_0', fontsize=11)
ax3.set_ylabel('Delta Psi (Psi - 1.01)', fontsize=11)
ax3.set_title('Distance to Threshold', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# ========================================
# Plot 4-6: Psi(t) buildup curves
# ========================================
# Select 3 representative cases: below, at, above threshold
test_alphas = [1.85, 1.90, 2.00]  # Below, at, above
colors_buildup = ['red', 'orange', 'green']

for idx, (alpha, color) in enumerate(zip(test_alphas, colors_buildup)):
    ax = plt.subplot(3, 3, 4 + idx)

    # Find data for this alpha
    data_for_alpha = [d for d in dynamic_data if abs(d['parameters']['alpha_0'] - alpha) < 0.01]

    if data_for_alpha:
        data = data_for_alpha[0]
        psi_hist = data['psi_history']

        times = [p['time'] for p in psi_hist]
        psis = [p['psi'] for p in psi_hist]
        committed = [p['committed'] for p in psi_hist]

        # Plot buildup
        ax.plot(times, psis, marker='.', linewidth=2, color=color, alpha=0.7)

        # Mark commits
        commit_points = [(t, p) for t, p, c in zip(times, psis, committed) if c]
        if commit_points:
            commit_times, commit_psis = zip(*commit_points)
            ax.scatter(commit_times, commit_psis, color='red', s=100, marker='X',
                      zorder=5, label='Commits')

        ax.axhline(y=1.01, color='red', linestyle='--', alpha=0.5, label='Threshold')
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Psi', fontsize=10)
        ax.set_title(f'Buildup: alpha_0={alpha:.2f}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if commit_points:
            ax.legend(fontsize=9)

# ========================================
# Plot 7: Threshold crossing time vs alpha_0
# ========================================
ax7 = plt.subplot(3, 3, 7)

crossing_data = [(d['parameters']['alpha_0'], d['statistics']['threshold_crossing_time'])
                 for d in dynamic_data
                 if d['statistics']['threshold_crossing_time'] is not None]

if crossing_data:
    alphas_cross, times_cross = zip(*crossing_data)
    ax7.plot(alphas_cross, times_cross, marker='o', linewidth=2, markersize=8, color='darkgreen')
    ax7.set_xlabel('alpha_0', fontsize=11)
    ax7.set_ylabel('Threshold Crossing Time (s)', fontsize=11)
    ax7.set_title('Time to First Commit', fontsize=12, fontweight='bold')
    ax7.grid(True, alpha=0.3)

# ========================================
# Plot 8: Buildup rate vs alpha_0
# ========================================
ax8 = plt.subplot(3, 3, 8)

rate_data = [(d['parameters']['alpha_0'], d['statistics']['buildup_rate'])
             for d in dynamic_data
             if d['statistics']['buildup_rate'] is not None]

if rate_data:
    alphas_rate, rates = zip(*rate_data)
    ax8.plot(alphas_rate, rates, marker='o', linewidth=2, markersize=8, color='darkblue')
    ax8.set_xlabel('alpha_0', fontsize=11)
    ax8.set_ylabel('dPsi/dt (1/s)', fontsize=11)
    ax8.set_title('Buildup Rate', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3)

    # Add power-law fit
    if len(rates) > 2:
        alphas_arr = np.array(alphas_rate)
        rates_arr = np.array(rates)
        log_coeffs = np.polyfit(np.log(alphas_arr), np.log(rates_arr), 1)
        exponent = log_coeffs[0]
        ax8.text(0.05, 0.95, f'dPsi/dt ~ alpha_0^{exponent:.2f}',
                transform=ax8.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# ========================================
# Plot 9: Commit count vs alpha_0
# ========================================
ax9 = plt.subplot(3, 3, 9)

commit_data = [(d['parameters']['alpha_0'], d['statistics']['agent_commit_count'])
               for d in dynamic_data]

alphas_commits, counts = zip(*commit_data)
ax9.bar(alphas_commits, counts, width=0.15, color='steelblue', alpha=0.7)
ax9.set_xlabel('alpha_0', fontsize=11)
ax9.set_ylabel('Total Commits', fontsize=11)
ax9.set_title('Commit Frequency', fontsize=12, fontweight='bold')
ax9.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('v3_comprehensive_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: v3_comprehensive_analysis.png")

# ========================================
# Additional plot: Zoomed threshold region
# ========================================
fig2, (ax_zoom1, ax_zoom2) = plt.subplots(1, 2, figsize=(14, 5))

# Zoom on has_commits
subset_zoom = df_ultra[(df_ultra['gamma'] == 0.001) &
                       (df_ultra['alpha_0'] >= 1.83) &
                       (df_ultra['alpha_0'] <= 1.92)]
subset_zoom = subset_zoom.sort_values('alpha_0')

ax_zoom1.plot(subset_zoom['alpha_0'], subset_zoom['has_commits'].astype(int),
              marker='o', linewidth=4, markersize=12, color='darkblue')
ax_zoom1.set_xlabel('alpha_0', fontsize=12)
ax_zoom1.set_ylabel('Has Commits (0/1)', fontsize=12)
ax_zoom1.set_title('Ultra-Fine Onset Detail\n(Resolution: 0.01)',
                   fontsize=13, fontweight='bold')
ax_zoom1.grid(True, alpha=0.4)
ax_zoom1.set_ylim(-0.1, 1.1)

# Zoom on final_psi
ax_zoom2.plot(subset_zoom['alpha_0'], subset_zoom['final_psi'],
              marker='o', linewidth=4, markersize=12, color='purple')
ax_zoom2.axhline(y=1.01, color='red', linestyle='--', linewidth=3, label='Threshold')
ax_zoom2.set_xlabel('alpha_0', fontsize=12)
ax_zoom2.set_ylabel('Final Psi', fontsize=12)
ax_zoom2.set_title('Salience vs Threshold\n(Critical Region)',
                   fontsize=13, fontweight='bold')
ax_zoom2.legend(fontsize=11)
ax_zoom2.grid(True, alpha=0.4)

# Annotate values
for idx, row in subset_zoom.iterrows():
    ax_zoom2.annotate(f"{row['final_psi']:.3f}",
                     (row['alpha_0'], row['final_psi']),
                     textcoords="offset points", xytext=(0,8),
                     ha='center', fontsize=8)

plt.tight_layout()
plt.savefig('v3_threshold_zoom.png', dpi=150, bbox_inches='tight')
print("Saved: v3_threshold_zoom.png")

plt.show()

print("\nVisualization complete!")
print("Generated files:")
print("  - v3_comprehensive_analysis.png (9-panel overview)")
print("  - v3_threshold_zoom.png (ultra-fine detail)")
