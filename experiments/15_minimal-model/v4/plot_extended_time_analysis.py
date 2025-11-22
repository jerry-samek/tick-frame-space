"""
Visualize extended time horizon results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
print("Loading data...")
df_threshold = pd.read_csv("extended_time_threshold_results.csv")
df_scaling = pd.read_csv("extended_time_scaling_results.csv")

# Create comprehensive figure
fig = plt.figure(figsize=(16, 10))

# ========================================
# Plot 1: Threshold stability across time horizons
# ========================================
ax1 = plt.subplot(2, 3, 1)

for T in sorted(df_threshold['T'].unique()):
    subset = df_threshold[df_threshold['T'] == T]
    subset = subset.sort_values('alpha_0')
    ax1.plot(subset['alpha_0'], subset['has_commits'].astype(int),
             marker='o', linewidth=2, markersize=8, label=f'T={T:.0f}s')

ax1.set_xlabel('alpha_0', fontsize=11)
ax1.set_ylabel('Has Commits (0/1)', fontsize=11)
ax1.set_title('Threshold Stability Across Time Horizons', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.1, 1.1)

# ========================================
# Plot 2: Final Psi vs alpha_0 for different T
# ========================================
ax2 = plt.subplot(2, 3, 2)

for T in sorted(df_threshold['T'].unique()):
    subset = df_threshold[df_threshold['T'] == T]
    subset = subset.sort_values('alpha_0')
    # Only plot cases without commits (to see Psi accumulation)
    subset_no_commits = subset[subset['has_commits'] == False]
    if len(subset_no_commits) > 0:
        ax2.plot(subset_no_commits['alpha_0'], subset_no_commits['final_psi'],
                marker='o', linewidth=2, markersize=6, label=f'T={T:.0f}s')

ax2.axhline(y=1.01, color='red', linestyle='--', linewidth=2, label='Threshold')
ax2.set_xlabel('alpha_0', fontsize=11)
ax2.set_ylabel('Final Psi', fontsize=11)
ax2.set_title('Psi Accumulation (No Commits)', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# ========================================
# Plot 3: Commit count vs T for different alpha_0
# ========================================
ax3 = plt.subplot(2, 3, 3)

colors = plt.cm.viridis(np.linspace(0, 1, len(df_scaling['alpha_0'].unique())))

for idx, alpha_0 in enumerate(sorted(df_scaling['alpha_0'].unique())):
    subset = df_scaling[df_scaling['alpha_0'] == alpha_0]
    subset = subset.sort_values('T')
    ax3.plot(subset['T'], subset['agent_commit_count'],
             marker='o', linewidth=2, markersize=8,
             label=f'alpha_0={alpha_0:.1f}', color=colors[idx])

ax3.set_xlabel('Time Horizon T (s)', fontsize=11)
ax3.set_ylabel('Total Commits', fontsize=11)
ax3.set_title('Commit Count Scaling', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# ========================================
# Plot 4: Commit rate vs T
# ========================================
ax4 = plt.subplot(2, 3, 4)

for idx, alpha_0 in enumerate(sorted(df_scaling['alpha_0'].unique())):
    subset = df_scaling[df_scaling['alpha_0'] == alpha_0]
    subset = subset.sort_values('T')
    ax4.plot(subset['T'], subset['commit_rate'],
             marker='o', linewidth=2, markersize=8,
             label=f'alpha_0={alpha_0:.1f}', color=colors[idx])

ax4.set_xlabel('Time Horizon T (s)', fontsize=11)
ax4.set_ylabel('Commit Rate (commits/s)', fontsize=11)
ax4.set_title('Commit Rate vs Time', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# ========================================
# Plot 5: Log-log scaling plot
# ========================================
ax5 = plt.subplot(2, 3, 5)

for idx, alpha_0 in enumerate(sorted(df_scaling['alpha_0'].unique())):
    subset = df_scaling[df_scaling['alpha_0'] == alpha_0]
    subset = subset.sort_values('T')

    # Only plot if we have commits
    subset_with_commits = subset[subset['agent_commit_count'] > 0]
    if len(subset_with_commits) > 1:
        ax5.loglog(subset_with_commits['T'], subset_with_commits['agent_commit_count'],
                   marker='o', linewidth=2, markersize=8,
                   label=f'alpha_0={alpha_0:.1f}', color=colors[idx])

        # Fit power law
        log_T = np.log(subset_with_commits['T'])
        log_N = np.log(subset_with_commits['agent_commit_count'])
        coeffs = np.polyfit(log_T, log_N, 1)
        beta = coeffs[0]

        # Plot fit line
        T_fit = np.array([subset_with_commits['T'].min(), subset_with_commits['T'].max()])
        N_fit = np.exp(coeffs[1]) * (T_fit ** beta)
        ax5.loglog(T_fit, N_fit, '--', color=colors[idx], alpha=0.5)

        # Annotate beta
        ax5.text(T_fit[0]*1.2, N_fit[0]*0.7, f'beta={beta:.2f}',
                fontsize=8, color=colors[idx])

ax5.set_xlabel('T (s)', fontsize=11)
ax5.set_ylabel('N_commits', fontsize=11)
ax5.set_title('Log-Log Scaling: N ~ T^beta', fontsize=12, fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3, which='both')

# ========================================
# Plot 6: Inter-commit intervals
# ========================================
ax6 = plt.subplot(2, 3, 6)

# Plot average commit intervals
for idx, alpha_0 in enumerate(sorted(df_scaling['alpha_0'].unique())):
    subset = df_scaling[df_scaling['alpha_0'] == alpha_0]
    subset = subset.sort_values('T')

    # Filter out NaN values
    subset_valid = subset[subset['avg_commit_interval'].notna()]
    if len(subset_valid) > 0:
        ax6.errorbar(subset_valid['T'], subset_valid['avg_commit_interval'],
                    yerr=subset_valid['std_commit_interval'],
                    marker='o', linewidth=2, markersize=6,
                    label=f'alpha_0={alpha_0:.1f}', color=colors[idx],
                    capsize=5)

ax6.set_xlabel('Time Horizon T (s)', fontsize=11)
ax6.set_ylabel('Avg Inter-Commit Interval (s)', fontsize=11)
ax6.set_title('Commit Timing Statistics', fontsize=12, fontweight='bold')
ax6.legend()
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('extended_time_comprehensive.png', dpi=150, bbox_inches='tight')
print("Saved: extended_time_comprehensive.png")

# ========================================
# Additional plot: Threshold stability detail
# ========================================
fig2, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Onset curves overlaid
for T in sorted(df_threshold['T'].unique()):
    subset = df_threshold[df_threshold['T'] == T]
    subset = subset.sort_values('alpha_0')
    ax_left.plot(subset['alpha_0'], subset['has_commits'].astype(int),
                marker='o', linewidth=3, markersize=10, label=f'T={T:.0f}s')

ax_left.set_xlabel('alpha_0', fontsize=12)
ax_left.set_ylabel('Has Commits (0/1)', fontsize=12)
ax_left.set_title('Threshold Stability Test\n(Overlaid Onset Curves)',
                  fontsize=13, fontweight='bold')
ax_left.legend(fontsize=11)
ax_left.grid(True, alpha=0.4)
ax_left.set_ylim(-0.1, 1.1)

# Right: Summary table as text
threshold_summary = []
for T in sorted(df_threshold['T'].unique()):
    subset = df_threshold[df_threshold['T'] == T]
    first_commit = subset[subset['has_commits'] == True]
    if len(first_commit) > 0:
        threshold = first_commit['alpha_0'].min()
        threshold_summary.append(f"T={T:5.0f}s: threshold at alpha_0 = {threshold:.2f}")
    else:
        threshold_summary.append(f"T={T:5.0f}s: no commits found")

# Plot as text
ax_right.axis('off')
text_str = "THRESHOLD SUMMARY\n" + "="*40 + "\n\n"
text_str += "\n".join(threshold_summary)

# Analyze if time-invariant
if len(threshold_summary) > 1:
    thresholds = []
    for T in sorted(df_threshold['T'].unique()):
        subset = df_threshold[df_threshold['T'] == T]
        first_commit = subset[subset['has_commits'] == True]
        if len(first_commit) > 0:
            thresholds.append(first_commit['alpha_0'].min())

    if len(set(thresholds)) == 1:
        conclusion = "\n\nCONCLUSION: TIME-INVARIANT\nThreshold does not shift with T"
    else:
        conclusion = f"\n\nCONCLUSION: TIME-DEPENDENT\nThreshold shifts: {min(thresholds):.2f} to {max(thresholds):.2f}"
    text_str += conclusion

ax_right.text(0.1, 0.5, text_str, fontsize=12, family='monospace',
              verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

plt.tight_layout()
plt.savefig('extended_time_threshold_stability.png', dpi=150, bbox_inches='tight')
print("Saved: extended_time_threshold_stability.png")

plt.show()

print("\nVisualization complete!")
print("Generated files:")
print("  - extended_time_comprehensive.png (6-panel overview)")
print("  - extended_time_threshold_stability.png (threshold detail)")
