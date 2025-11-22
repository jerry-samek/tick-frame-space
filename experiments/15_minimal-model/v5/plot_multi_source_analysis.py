"""
Visualize multi-source experiment results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Check which result files exist
files_to_plot = {}

if os.path.exists("phase_a_geometry_results.csv"):
    files_to_plot['phase_a'] = pd.read_csv("phase_a_geometry_results.csv")
    print("Loaded Phase A results")

if os.path.exists("phase_d_interference_results.csv"):
    files_to_plot['phase_d'] = pd.read_csv("phase_d_interference_results.csv")
    print("Loaded Phase D results")

if not files_to_plot:
    print("No result files found. Run experiments first.")
    exit(1)

# ========================================
# Phase A: Geometry and Source Count
# ========================================

if 'phase_a' in files_to_plot:
    df_a = files_to_plot['phase_a']

    fig_a = plt.figure(figsize=(16, 10))

    # Plot 1: Threshold vs source count (T=100s, symmetric)
    ax1 = plt.subplot(2, 3, 1)

    subset = df_a[(df_a['T'] == 100.0) & (df_a['geometry'] == 'symmetric')]

    for num_sources in sorted(subset['num_sources'].unique()):
        data = subset[subset['num_sources'] == num_sources]
        data = data.sort_values('alpha_0')
        ax1.plot(data['alpha_0'], data['has_commits'].astype(int),
                marker='o', linewidth=2, markersize=8,
                label=f'M_s={num_sources}')

    ax1.set_xlabel('alpha_0', fontsize=11)
    ax1.set_ylabel('Has Commits (0/1)', fontsize=11)
    ax1.set_title('Threshold vs Source Count (Symmetric, T=100s)',
                  fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.1, 1.1)

    # Plot 2: Threshold scaling analysis
    ax2 = plt.subplot(2, 3, 2)

    thresholds = []
    source_counts = []

    for num_sources in sorted(df_a['num_sources'].unique()):
        matching = df_a[(df_a['num_sources'] == num_sources) &
                       (df_a['geometry'] == 'symmetric') &
                       (df_a['T'] == 100.0) &
                       (df_a['has_commits'] == True)]
        if len(matching) > 0:
            threshold = matching['alpha_0'].min()
            thresholds.append(threshold)
            source_counts.append(num_sources)

    if thresholds:
        ax2.plot(source_counts, thresholds, 'o-', linewidth=2, markersize=10,
                label='Measured', color='blue')

        # Theoretical M_s^(-1/2) scaling
        if thresholds:
            baseline = thresholds[0]
            theoretical = [baseline / np.sqrt(m) for m in source_counts]
            ax2.plot(source_counts, theoretical, '--', linewidth=2,
                    label='Theoretical M_s^(-1/2)', color='red', alpha=0.7)

    ax2.set_xlabel('Number of Sources M_s', fontsize=11)
    ax2.set_ylabel('alpha_0_threshold', fontsize=11)
    ax2.set_title('Threshold Scaling Law', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Geometry comparison (T=100s)
    ax3 = plt.subplot(2, 3, 3)

    for geometry in ['symmetric', 'asymmetric']:
        thresholds = []
        source_counts = []

        for num_sources in sorted(df_a['num_sources'].unique()):
            matching = df_a[(df_a['num_sources'] == num_sources) &
                           (df_a['geometry'] == geometry) &
                           (df_a['T'] == 100.0) &
                           (df_a['has_commits'] == True)]
            if len(matching) > 0:
                threshold = matching['alpha_0'].min()
                thresholds.append(threshold)
                source_counts.append(num_sources)

        if thresholds:
            ax3.plot(source_counts, thresholds, 'o-', linewidth=2,
                    markersize=8, label=geometry.capitalize())

    ax3.set_xlabel('Number of Sources M_s', fontsize=11)
    ax3.set_ylabel('alpha_0_threshold', fontsize=11)
    ax3.set_title('Symmetric vs Asymmetric Layout', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Commit counts for different source counts (T=200s, alpha_0=2.0)
    ax4 = plt.subplot(2, 3, 4)

    subset = df_a[(df_a['T'] == 200.0) &
                  (abs(df_a['alpha_0'] - 2.0) < 0.01) &
                  (df_a['geometry'] == 'symmetric')]

    if len(subset) > 0:
        source_counts = subset['num_sources'].values
        commit_counts = subset['agent_commit_count'].values

        ax4.bar(source_counts, commit_counts, width=0.6, alpha=0.7, color='steelblue')
        ax4.set_xlabel('Number of Sources M_s', fontsize=11)
        ax4.set_ylabel('Total Commits', fontsize=11)
        ax4.set_title('Commit Count at alpha_0=2.0, T=200s', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

    # Plot 5: Time horizon comparison (M_s=2, symmetric)
    ax5 = plt.subplot(2, 3, 5)

    subset = df_a[(df_a['num_sources'] == 2) & (df_a['geometry'] == 'symmetric')]

    for T in sorted(subset['T'].unique()):
        data = subset[subset['T'] == T]
        data = data.sort_values('alpha_0')
        ax5.plot(data['alpha_0'], data['has_commits'].astype(int),
                marker='o', linewidth=2, markersize=8, label=f'T={T:.0f}s')

    ax5.set_xlabel('alpha_0', fontsize=11)
    ax5.set_ylabel('Has Commits (0/1)', fontsize=11)
    ax5.set_title('Time Horizon Effect (M_s=2, Symmetric)', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim(-0.1, 1.1)

    # Plot 6: Salience comparison
    ax6 = plt.subplot(2, 3, 6)

    subset = df_a[(df_a['T'] == 100.0) & (df_a['geometry'] == 'symmetric')]

    for num_sources in sorted(subset['num_sources'].unique()):
        data = subset[subset['num_sources'] == num_sources]
        data = data.sort_values('alpha_0')
        # Only plot cases without commits to see accumulation
        no_commits = data[data['has_commits'] == False]
        if len(no_commits) > 0:
            ax6.plot(no_commits['alpha_0'], no_commits['final_psi'],
                    marker='o', linewidth=2, markersize=6,
                    label=f'M_s={num_sources}')

    ax6.axhline(y=1.01, color='red', linestyle='--', linewidth=2, label='Threshold')
    ax6.set_xlabel('alpha_0', fontsize=11)
    ax6.set_ylabel('Final Psi', fontsize=11)
    ax6.set_title('Psi Accumulation (No Commits)', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('phase_a_comprehensive.png', dpi=150, bbox_inches='tight')
    print("Saved: phase_a_comprehensive.png")

# ========================================
# Phase D: Interference Effects
# ========================================

if 'phase_d' in files_to_plot:
    df_d = files_to_plot['phase_d']

    fig_d = plt.figure(figsize=(14, 10))

    # Plot 1: Threshold vs phase offset
    ax1 = plt.subplot(2, 2, 1)

    for phase_offset in sorted(df_d['phase_offset'].unique()):
        data = df_d[df_d['phase_offset'] == phase_offset]
        data = data.sort_values('alpha_0')
        label = f'Phase={phase_offset}'
        if phase_offset == 0:
            label += ' (in-phase)'
        elif phase_offset == 1:
            label += ' (anti-phase)'
        ax1.plot(data['alpha_0'], data['has_commits'].astype(int),
                marker='o', linewidth=2, markersize=8, label=label)

    ax1.set_xlabel('alpha_0', fontsize=11)
    ax1.set_ylabel('Has Commits (0/1)', fontsize=11)
    ax1.set_title('Phase Effect on Threshold', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.1, 1.1)

    # Plot 2: Commit counts vs phase
    ax2 = plt.subplot(2, 2, 2)

    # Use alpha_0=2.0 as test case
    subset = df_d[abs(df_d['alpha_0'] - 2.0) < 0.01]

    if len(subset) > 0:
        phases = subset['phase_offset'].values
        commits = subset['agent_commit_count'].values

        ax2.bar(phases, commits, width=0.4, alpha=0.7, color='steelblue')
        ax2.set_xlabel('Phase Offset (ticks)', fontsize=11)
        ax2.set_ylabel('Total Commits', fontsize=11)
        ax2.set_title('Commit Count at alpha_0=2.0', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Commit rate vs phase
    ax3 = plt.subplot(2, 2, 3)

    for phase_offset in sorted(df_d['phase_offset'].unique()):
        data = df_d[df_d['phase_offset'] == phase_offset]
        data = data[data['has_commits'] == True]
        data = data.sort_values('alpha_0')

        if len(data) > 0:
            label = f'Phase={phase_offset}'
            ax3.plot(data['alpha_0'], data['commit_rate'],
                    marker='o', linewidth=2, markersize=6, label=label)

    ax3.set_xlabel('alpha_0', fontsize=11)
    ax3.set_ylabel('Commit Rate (commits/s)', fontsize=11)
    ax3.set_title('Commit Rate vs Phase', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Interference factor summary
    ax4 = plt.subplot(2, 2, 4)

    thresholds = []
    phases = []

    for phase_offset in sorted(df_d['phase_offset'].unique()):
        matching = df_d[(df_d['phase_offset'] == phase_offset) &
                       (df_d['has_commits'] == True)]
        if len(matching) > 0:
            threshold = matching['alpha_0'].min()
            thresholds.append(threshold)
            phases.append(phase_offset)

    if thresholds:
        baseline = thresholds[0]
        kappas = [t / baseline for t in thresholds]

        colors = ['green' if k < 1.0 else 'red' for k in kappas]
        ax4.bar(phases, kappas, width=0.4, color=colors, alpha=0.7)
        ax4.axhline(y=1.0, color='black', linestyle='--', linewidth=2,
                   label='Baseline (in-phase)')
        ax4.set_xlabel('Phase Offset (ticks)', fontsize=11)
        ax4.set_ylabel('Interference Factor kappa', fontsize=11)
        ax4.set_title('Interference Strength', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('phase_d_interference.png', dpi=150, bbox_inches='tight')
    print("Saved: phase_d_interference.png")

plt.show()

print("\nVisualization complete!")
print("Generated files:")
if 'phase_a' in files_to_plot:
    print("  - phase_a_comprehensive.png (6-panel overview)")
if 'phase_d' in files_to_plot:
    print("  - phase_d_interference.png (4-panel overview)")
