"""
Visualize the refined boundary sweep results.
Creates plots showing the onset curve with high resolution.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load refined boundary results
df = pd.read_csv("refined_boundary_results.csv")

# Convert has_commits boolean to numeric
df['has_commits_num'] = df['has_commits'].astype(int)

# Create figure with multiple subplots
fig = plt.figure(figsize=(16, 10))

# ========================================
# Plot 1: Onset curve for M=1, varying gamma
# ========================================
ax1 = plt.subplot(2, 3, 1)
for gamma in sorted(df['gamma'].unique()):
    subset = df[(df['M'] == 1) & (df['gamma'] == gamma)]
    subset = subset.sort_values('alpha_0')
    ax1.plot(subset['alpha_0'], subset['has_commits_num'],
             marker='o', label=f'gamma={gamma:.4f}', linewidth=2)

ax1.set_xlabel('alpha_0 (emission strength)', fontsize=11)
ax1.set_ylabel('Has Commits (0=No, 1=Yes)', fontsize=11)
ax1.set_title('Onset Curve: M=1, Varying Damping', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.1, 1.1)

# ========================================
# Plot 2: Final Psi accumulation (M=1, gamma=0.001)
# ========================================
ax2 = plt.subplot(2, 3, 2)
subset = df[(df['M'] == 1) & (df['gamma'] == 0.001)]
subset = subset.sort_values('alpha_0')
ax2.plot(subset['alpha_0'], subset['final_psi'], marker='o', linewidth=2, color='purple')
ax2.axhline(y=1.01, color='red', linestyle='--', label='Commit threshold (1.01)')
ax2.set_xlabel('alpha_0 (emission strength)', fontsize=11)
ax2.set_ylabel('Final Psi (accumulated salience)', fontsize=11)
ax2.set_title('Salience Accumulation: M=1, gamma=0.001', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
# Annotate the threshold crossing
threshold_crossing = subset[subset['final_psi'] >= 1.01]['alpha_0'].min()
if not pd.isna(threshold_crossing):
    ax2.annotate(f'Threshold\ncrossing\nat {threshold_crossing:.2f}',
                xy=(threshold_crossing, 1.01), xytext=(threshold_crossing-0.15, 1.3),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, ha='center', color='red', fontweight='bold')

# ========================================
# Plot 3: Max salience vs alpha_0 (M=1, gamma=0.001)
# ========================================
ax3 = plt.subplot(2, 3, 3)
subset = df[(df['M'] == 1) & (df['gamma'] == 0.001)]
subset = subset.sort_values('alpha_0')
ax3.plot(subset['alpha_0'], subset['max_salience'], marker='o', linewidth=2, color='green')
ax3.set_xlabel('alpha_0 (emission strength)', fontsize=11)
ax3.set_ylabel('Max Salience', fontsize=11)
ax3.set_title('Peak Salience: M=1, gamma=0.001', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# ========================================
# Plot 4: Effect of sampling rate M (gamma=0.001)
# ========================================
ax4 = plt.subplot(2, 3, 4)
for M in sorted(df['M'].unique()):
    subset = df[(df['M'] == M) & (df['gamma'] == 0.001)]
    subset = subset.sort_values('alpha_0')
    ax4.plot(subset['alpha_0'], subset['final_psi'],
             marker='o', label=f'M={M}', linewidth=2)

ax4.axhline(y=1.01, color='red', linestyle='--', label='Commit threshold')
ax4.set_xlabel('alpha_0 (emission strength)', fontsize=11)
ax4.set_ylabel('Final Psi', fontsize=11)
ax4.set_title('Sampling Effect: gamma=0.001, Varying M', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# ========================================
# Plot 5: Threshold surface (M=1)
# ========================================
ax5 = plt.subplot(2, 3, 5)
# Create a pivot table for thresholds
threshold_data = []
for gamma in sorted(df['gamma'].unique()):
    subset = df[(df['M'] == 1) & (df['gamma'] == gamma)]
    # Find minimum alpha_0 where commits occur
    commits_subset = subset[subset['has_commits'] == True]
    if len(commits_subset) > 0:
        threshold = commits_subset['alpha_0'].min()
        threshold_data.append({'gamma': gamma, 'threshold_alpha0': threshold})
    else:
        threshold_data.append({'gamma': gamma, 'threshold_alpha0': np.nan})

threshold_df = pd.DataFrame(threshold_data)
ax5.plot(threshold_df['gamma'], threshold_df['threshold_alpha0'],
         marker='o', linewidth=2, markersize=10, color='darkblue')
ax5.set_xlabel('gamma (damping)', fontsize=11)
ax5.set_ylabel('Threshold alpha_0', fontsize=11)
ax5.set_title('Threshold vs Damping (M=1)', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.set_xlim(0, max(threshold_df['gamma'])*1.1)

# ========================================
# Plot 6: Phase diagram (has commits vs no commits)
# ========================================
ax6 = plt.subplot(2, 3, 6)
# Plot for M=1 only
subset_m1 = df[df['M'] == 1]
for has_commits in [False, True]:
    data = subset_m1[subset_m1['has_commits'] == has_commits]
    marker = 'X' if has_commits else 'o'
    label = 'Commits' if has_commits else 'No Commits'
    color = 'green' if has_commits else 'red'
    ax6.scatter(data['gamma'], data['alpha_0'], marker=marker, s=100,
                label=label, alpha=0.6, color=color)

ax6.set_xlabel('gamma (damping)', fontsize=11)
ax6.set_ylabel('alpha_0 (emission strength)', fontsize=11)
ax6.set_title('Phase Diagram: M=1', fontsize=12, fontweight='bold')
ax6.legend()
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('refined_boundary_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: refined_boundary_analysis.png")

# ========================================
# Additional plot: Zoom on critical region
# ========================================
fig2, (ax_zoom1, ax_zoom2) = plt.subplots(1, 2, figsize=(14, 5))

# Zoom on final_psi near threshold
subset_zoom = df[(df['M'] == 1) & (df['gamma'] == 0.001)]
subset_zoom = subset_zoom.sort_values('alpha_0')
ax_zoom1.plot(subset_zoom['alpha_0'], subset_zoom['final_psi'],
              marker='o', linewidth=3, markersize=10, color='purple')
ax_zoom1.axhline(y=1.01, color='red', linestyle='--', linewidth=2, label='Threshold')
ax_zoom1.set_xlabel('alpha_0', fontsize=12)
ax_zoom1.set_ylabel('Final Psi', fontsize=12)
ax_zoom1.set_title('Critical Region: Final Psi near Threshold\n(M=1, gamma=0.001)',
                   fontsize=13, fontweight='bold')
ax_zoom1.legend(fontsize=11)
ax_zoom1.grid(True, alpha=0.4)
ax_zoom1.set_xlim(1.75, 2.0)
ax_zoom1.set_ylim(0.8, 1.1)

# Add data labels
for idx, row in subset_zoom.iterrows():
    if 1.75 <= row['alpha_0'] <= 2.0:
        ax_zoom1.annotate(f"{row['final_psi']:.3f}",
                         (row['alpha_0'], row['final_psi']),
                         textcoords="offset points", xytext=(0,8),
                         ha='center', fontsize=8)

# Zoom on onset boundary
for gamma in [0.005, 0.001, 0.0005]:
    subset = df[(df['M'] == 1) & (df['gamma'] == gamma)]
    subset = subset.sort_values('alpha_0')
    ax_zoom2.plot(subset['alpha_0'], subset['has_commits_num'],
                  marker='o', linewidth=3, markersize=10,
                  label=f'gamma={gamma:.4f}')

ax_zoom2.set_xlabel('alpha_0', fontsize=12)
ax_zoom2.set_ylabel('Has Commits (0/1)', fontsize=12)
ax_zoom2.set_title('Onset Boundary Detail\n(M=1, Low Damping)',
                   fontsize=13, fontweight='bold')
ax_zoom2.legend(fontsize=11)
ax_zoom2.grid(True, alpha=0.4)
ax_zoom2.set_xlim(1.75, 2.0)
ax_zoom2.set_ylim(-0.1, 1.1)

plt.tight_layout()
plt.savefig('refined_boundary_zoom.png', dpi=150, bbox_inches='tight')
print("Saved: refined_boundary_zoom.png")

plt.show()

print("\nVisualization complete!")
print("Generated files:")
print("  - refined_boundary_analysis.png (6-panel overview)")
print("  - refined_boundary_zoom.png (detailed critical region)")
