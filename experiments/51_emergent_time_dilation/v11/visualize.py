#!/usr/bin/env python3
"""
Visualization Module for Experiment 51i (V9)

Static and animated visualizations of time dilation fields and entity dynamics.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle
from typing import List, Tuple, Optional
import matplotlib.colors as mcolors

from entity_motion import MovingEntity, StationaryEntity
from field_dynamics import FieldDynamics
from analysis import analyze_entity_time_dilation


# ============================================================================
# Static Visualizations
# ============================================================================

def plot_field_heatmap(
    field: np.ndarray,
    title: str = "Field",
    planet_center: Tuple[float, float] = (50.0, 50.0),
    planet_radius: float = 10.0,
    cmap: str = 'viridis',
    vmin: float = None,
    vmax: float = None,
    save_path: str = None
):
    """
    Plot 2D heatmap of field.

    Args:
        field: 2D numpy array
        title: Plot title
        planet_center: (cx, cy) center for reference
        planet_radius: Radius to mark on plot
        cmap: Colormap name
        vmin, vmax: Color scale limits
        save_path: If provided, save figure to path
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(
        field.T,
        origin='lower',
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        extent=[0, field.shape[0], 0, field.shape[1]],
        interpolation='bilinear'
    )

    # Mark planet region
    circle = Circle(
        planet_center,
        planet_radius,
        fill=False,
        edgecolor='red',
        linewidth=2,
        linestyle='--',
        label='Planet cluster'
    )
    ax.add_patch(circle)

    # Mark center
    ax.plot(planet_center[0], planet_center[1], 'r+', markersize=15, markeredgewidth=2)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.legend()
    ax.set_aspect('equal')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(title.split('(')[0].strip())

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_gamma_field(
    fields: FieldDynamics,
    planet_center: Tuple[float, float] = (50.0, 50.0),
    planet_radius: float = 10.0,
    save_path: str = None
):
    """Plot gravitational time dilation field."""
    gamma_field = fields.get_gamma_grav()

    return plot_field_heatmap(
        gamma_field,
        title='Gravitational Time Dilation (γ_grav)',
        planet_center=planet_center,
        planet_radius=planet_radius,
        cmap='plasma',
        vmin=1.0,
        vmax=np.percentile(gamma_field, 99),
        save_path=save_path
    )


def plot_load_energy_fields(
    fields: FieldDynamics,
    planet_center: Tuple[float, float] = (50.0, 50.0),
    planet_radius: float = 10.0,
    save_path: str = None
):
    """Plot load and energy fields side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Load field
    im1 = axes[0].imshow(
        fields.state.L.T,
        origin='lower',
        cmap='hot',
        extent=[0, fields.grid_size, 0, fields.grid_size],
        interpolation='bilinear'
    )
    axes[0].set_title('Load Field (L)', fontsize=14)
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    plt.colorbar(im1, ax=axes[0], label='Load')

    # Energy field
    im2 = axes[1].imshow(
        fields.state.E.T,
        origin='lower',
        cmap='viridis',
        extent=[0, fields.grid_size, 0, fields.grid_size],
        interpolation='bilinear'
    )
    axes[1].set_title('Energy Field (E)', fontsize=14)
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('y')
    plt.colorbar(im2, ax=axes[1], label='Energy')

    # Mark planet on both
    for ax in axes:
        circle = Circle(
            planet_center,
            planet_radius,
            fill=False,
            edgecolor='cyan',
            linewidth=2,
            linestyle='--'
        )
        ax.add_patch(circle)
        ax.plot(planet_center[0], planet_center[1], 'c+', markersize=12, markeredgewidth=2)
        ax.set_aspect('equal')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, axes


def plot_entity_trajectories(
    entities: List[MovingEntity],
    fields: FieldDynamics,
    planet_center: Tuple[float, float] = (50.0, 50.0),
    planet_radius: float = 10.0,
    save_path: str = None
):
    """
    Plot entity trajectories colored by local gamma_eff.

    Args:
        entities: List of mobile entities
        fields: Field dynamics for background
        planet_center: (cx, cy) center
        planet_radius: Radius to mark
        save_path: If provided, save figure
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Background: gamma field
    gamma_field = fields.get_gamma_grav()
    im = ax.imshow(
        gamma_field.T,
        origin='lower',
        cmap='gray',
        alpha=0.3,
        extent=[0, fields.grid_size, 0, fields.grid_size],
        interpolation='bilinear',
        vmin=1.0,
        vmax=np.percentile(gamma_field, 95)
    )

    # Plot trajectories
    cmap = plt.get_cmap('plasma')
    norm = mcolors.Normalize(vmin=1.0, vmax=10.0)

    for entity in entities:
        if len(entity.position_history) < 2:
            continue

        positions = np.array(entity.position_history)
        gamma_eff = entity.gamma_eff_measured

        # Color by gamma_eff
        color = cmap(norm(gamma_eff))

        ax.plot(
            positions[:, 0],
            positions[:, 1],
            color=color,
            alpha=0.7,
            linewidth=1.5,
            label=f"{entity.entity_id} (γ={gamma_eff:.2f})"
        )

        # Mark start and end
        ax.plot(positions[0, 0], positions[0, 1], 'go', markersize=5)
        ax.plot(positions[-1, 0], positions[-1, 1], 'rs', markersize=5)

    # Mark planet
    circle = Circle(
        planet_center,
        planet_radius,
        fill=False,
        edgecolor='red',
        linewidth=2,
        linestyle='--',
        label='Planet cluster'
    )
    ax.add_patch(circle)
    ax.plot(planet_center[0], planet_center[1], 'r+', markersize=15, markeredgewidth=2)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Entity Trajectories (colored by γ_eff)')
    ax.set_aspect('equal')

    # Colorbar for gamma_eff
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('γ_eff')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_gamma_vs_distance(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float] = (50.0, 50.0),
    save_path: str = None
):
    """
    Plot gamma_eff vs distance from planet.

    Args:
        entities: List of entities
        planet_center: (cx, cy) center
        save_path: If provided, save figure
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Compute distances and gammas
    distances = []
    gamma_effs = []
    gamma_gravs = []
    speeds = []

    for entity in entities:
        decomp = analyze_entity_time_dilation(entity, planet_center)
        distances.append(decomp.avg_distance)
        gamma_effs.append(decomp.gamma_eff_measured)
        gamma_gravs.append(decomp.gamma_grav_avg)
        speeds.append(entity.speed)

    distances = np.array(distances)
    gamma_effs = np.array(gamma_effs)
    gamma_gravs = np.array(gamma_gravs)
    speeds = np.array(speeds)

    # Color by speed
    cmap = plt.get_cmap('viridis')
    norm = mcolors.Normalize(vmin=0.0, vmax=1.0)

    scatter = ax.scatter(
        distances,
        gamma_effs,
        c=speeds,
        cmap=cmap,
        norm=norm,
        s=80,
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        label='γ_eff (measured)'
    )

    # Also plot gamma_grav
    ax.scatter(
        distances,
        gamma_gravs,
        marker='x',
        s=60,
        color='red',
        alpha=0.5,
        label='γ_grav (gravitational only)'
    )

    ax.set_xlabel('Distance from Planet Center', fontsize=12)
    ax.set_ylabel('Time Dilation Factor (γ)', fontsize=12)
    ax.set_title('Time Dilation vs Distance', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Colorbar for speed
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Speed (v/c)')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_gamma_vs_velocity(
    entities: List[MovingEntity],
    planet_center: Tuple[float, float] = (50.0, 50.0),
    save_path: str = None
):
    """
    Plot gamma_eff vs velocity to validate Lorentz factor.

    Args:
        entities: List of entities
        planet_center: (cx, cy) center
        save_path: If provided, save figure
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Collect data
    speeds = []
    gamma_SR_measured = []
    gamma_SR_predicted = []

    for entity in entities:
        speeds.append(entity.speed)

        # Measured (from history)
        if len(entity.gamma_SR_history) > 0:
            gamma_SR_measured.append(np.mean(entity.gamma_SR_history))
        else:
            gamma_SR_measured.append(entity.gamma_SR)

        # Predicted: 1/sqrt(1 - v^2)
        v = entity.speed
        gamma_predicted = 1.0 / np.sqrt(1.0 - v**2) if v < 0.9999 else 10.0
        gamma_SR_predicted.append(gamma_predicted)

    speeds = np.array(speeds)
    gamma_SR_measured = np.array(gamma_SR_measured)
    gamma_SR_predicted = np.array(gamma_SR_predicted)

    # Theoretical curve
    v_theory = np.linspace(0, 0.995, 100)
    gamma_theory = 1.0 / np.sqrt(1.0 - v_theory**2)

    ax.plot(v_theory, gamma_theory, 'k--', linewidth=2, label='Theory: γ_SR = 1/√(1-v²/c²)', alpha=0.7)

    # Measured points
    ax.scatter(
        speeds,
        gamma_SR_measured,
        s=80,
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        label='Measured γ_SR'
    )

    ax.set_xlabel('Velocity (v/c)', fontsize=12)
    ax.set_ylabel('Lorentz Factor (γ_SR)', fontsize=12)
    ax.set_title('Special Relativistic Time Dilation vs Velocity', fontsize=14)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0.9, max(gamma_theory.max(), gamma_SR_measured.max()) * 1.1)
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_summary_dashboard(
    entities: List[MovingEntity],
    fields: FieldDynamics,
    planet_center: Tuple[float, float] = (50.0, 50.0),
    planet_radius: float = 10.0,
    save_path: str = None
):
    """
    Create comprehensive summary dashboard with multiple subplots.

    Args:
        entities: Mobile entities
        fields: Field dynamics
        planet_center: (cx, cy) center
        planet_radius: Radius
        save_path: If provided, save figure
    """
    fig = plt.figure(figsize=(18, 12))

    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Gamma field (top-left)
    ax1 = fig.add_subplot(gs[0, 0])
    gamma_field = fields.get_gamma_grav()
    im1 = ax1.imshow(
        gamma_field.T,
        origin='lower',
        cmap='plasma',
        vmin=1.0,
        vmax=np.percentile(gamma_field, 99),
        extent=[0, fields.grid_size, 0, fields.grid_size]
    )
    circle1 = Circle(planet_center, planet_radius, fill=False, edgecolor='white', linewidth=2, linestyle='--')
    ax1.add_patch(circle1)
    ax1.set_title('γ_grav Field')
    ax1.set_aspect('equal')
    plt.colorbar(im1, ax=ax1)

    # 2. Load field (top-middle)
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(
        fields.state.L.T,
        origin='lower',
        cmap='hot',
        extent=[0, fields.grid_size, 0, fields.grid_size]
    )
    circle2 = Circle(planet_center, planet_radius, fill=False, edgecolor='cyan', linewidth=2, linestyle='--')
    ax2.add_patch(circle2)
    ax2.set_title('Load Field (L)')
    ax2.set_aspect('equal')
    plt.colorbar(im2, ax=ax2)

    # 3. Energy field (top-right)
    ax3 = fig.add_subplot(gs[0, 2])
    im3 = ax3.imshow(
        fields.state.E.T,
        origin='lower',
        cmap='viridis',
        extent=[0, fields.grid_size, 0, fields.grid_size]
    )
    circle3 = Circle(planet_center, planet_radius, fill=False, edgecolor='white', linewidth=2, linestyle='--')
    ax3.add_patch(circle3)
    ax3.set_title('Energy Field (E)')
    ax3.set_aspect('equal')
    plt.colorbar(im3, ax=ax3)

    # 4. Trajectories (middle-left)
    ax4 = fig.add_subplot(gs[1, 0])
    gamma_bg = fields.get_gamma_grav()
    ax4.imshow(gamma_bg.T, origin='lower', cmap='gray', alpha=0.2, extent=[0, fields.grid_size, 0, fields.grid_size])
    for entity in entities[:10]:  # Limit to 10 for clarity
        if len(entity.position_history) > 1:
            positions = np.array(entity.position_history)
            ax4.plot(positions[:, 0], positions[:, 1], alpha=0.6, linewidth=1)
    circle4 = Circle(planet_center, planet_radius, fill=False, edgecolor='red', linewidth=2)
    ax4.add_patch(circle4)
    ax4.set_title('Entity Trajectories')
    ax4.set_aspect('equal')

    # 5. Gamma vs distance (middle-center and middle-right combined)
    ax5 = fig.add_subplot(gs[1, 1:])
    distances = []
    gamma_effs = []
    speeds = []
    for entity in entities:
        decomp = analyze_entity_time_dilation(entity, planet_center)
        distances.append(decomp.avg_distance)
        gamma_effs.append(decomp.gamma_eff_measured)
        speeds.append(entity.speed)
    scatter5 = ax5.scatter(distances, gamma_effs, c=speeds, cmap='viridis', s=60, alpha=0.7)
    ax5.set_xlabel('Distance from Planet')
    ax5.set_ylabel('γ_eff')
    ax5.set_title('Time Dilation vs Distance')
    ax5.grid(True, alpha=0.3)
    plt.colorbar(scatter5, ax=ax5, label='Speed (v/c)')

    # 6. Gamma vs velocity (bottom-left and bottom-middle combined)
    ax6 = fig.add_subplot(gs[2, :2])
    v_theory = np.linspace(0, 0.995, 100)
    gamma_theory = 1.0 / np.sqrt(1.0 - v_theory**2)
    ax6.plot(v_theory, gamma_theory, 'k--', linewidth=2, label='Theory')
    speeds_arr = np.array(speeds)
    gamma_SR = [np.mean(e.gamma_SR_history) if e.gamma_SR_history else e.gamma_SR for e in entities]
    ax6.scatter(speeds_arr, gamma_SR, s=60, alpha=0.7, label='Measured')
    ax6.set_xlabel('Velocity (v/c)')
    ax6.set_ylabel('γ_SR')
    ax6.set_title('Lorentz Factor Validation')
    ax6.grid(True, alpha=0.3)
    ax6.legend()

    # 7. Proper time comparison (bottom-right)
    ax7 = fig.add_subplot(gs[2, 2])
    proper_times = [e.proper_time for e in entities]
    coordinate_times = [e.coordinate_time for e in entities]
    gamma_measured = [ct/pt if pt > 0 else 1.0 for ct, pt in zip(coordinate_times, proper_times)]
    ax7.hist(gamma_measured, bins=20, alpha=0.7, edgecolor='black')
    ax7.set_xlabel('γ_eff (measured)')
    ax7.set_ylabel('Count')
    ax7.set_title('Distribution of Time Dilation')
    ax7.grid(True, alpha=0.3)

    fig.suptitle('Experiment 51i (V9) - Summary Dashboard', fontsize=16, fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig


# ============================================================================
# Animated Visualizations
# ============================================================================

def create_animation(
    experiment,
    output_path: str = "v9_animation.gif",
    fps: int = 10,
    max_frames: int = 100
):
    """
    Create animated visualization of simulation.

    Args:
        experiment: Experiment51i instance with snapshots
        output_path: Path to save animation
        fps: Frames per second
        max_frames: Maximum number of frames
    """
    if len(experiment.snapshots) == 0:
        print("No snapshots to animate!")
        return

    snapshots = experiment.snapshots[:max_frames]

    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # Create subplots
    ax_gamma = fig.add_subplot(gs[:, 0])
    ax_load = fig.add_subplot(gs[0, 1])
    ax_energy = fig.add_subplot(gs[0, 2])
    ax_trajectories = fig.add_subplot(gs[1, 1])
    ax_times = fig.add_subplot(gs[1, 2])

    planet_center = experiment.config.entities.planet_center
    planet_radius = experiment.config.entities.planet_radius

    def update(frame_idx):
        snapshot = snapshots[frame_idx]
        tick = snapshot.tick

        # Clear axes
        for ax in [ax_gamma, ax_load, ax_energy, ax_trajectories, ax_times]:
            ax.clear()

        # Gamma field
        gamma_field = experiment.fields.get_gamma_grav()
        im1 = ax_gamma.imshow(
            gamma_field.T,
            origin='lower',
            cmap='plasma',
            vmin=1.0,
            vmax=5.0,
            extent=[0, experiment.config.simulation.grid_size, 0, experiment.config.simulation.grid_size]
        )
        circle = Circle(planet_center, planet_radius, fill=False, edgecolor='white', linewidth=2)
        ax_gamma.add_patch(circle)

        # Plot current entity positions
        for entity_state in snapshot.entity_states:
            pos = entity_state['position']
            ax_gamma.plot(pos[0], pos[1], 'wo', markersize=4)

        ax_gamma.set_title(f'γ_grav Field (Tick {tick})')
        ax_gamma.set_aspect('equal')

        # Load field
        im2 = ax_load.imshow(
            experiment.fields.state.L.T,
            origin='lower',
            cmap='hot',
            extent=[0, experiment.config.simulation.grid_size, 0, experiment.config.simulation.grid_size]
        )
        ax_load.set_title('Load Field')
        ax_load.set_aspect('equal')

        # Energy field
        im3 = ax_energy.imshow(
            experiment.fields.state.E.T,
            origin='lower',
            cmap='viridis',
            extent=[0, experiment.config.simulation.grid_size, 0, experiment.config.simulation.grid_size]
        )
        ax_energy.set_title('Energy Field')
        ax_energy.set_aspect('equal')

        # Trajectories (accumulated)
        for entity in experiment.mobile_entities:
            if len(entity.position_history) > 1:
                positions = np.array(entity.position_history[:frame_idx * 10])
                if len(positions) > 1:
                    ax_trajectories.plot(positions[:, 0], positions[:, 1], alpha=0.5, linewidth=1)
        circle_traj = Circle(planet_center, planet_radius, fill=False, edgecolor='red', linewidth=2)
        ax_trajectories.add_patch(circle_traj)
        ax_trajectories.set_title('Trajectories')
        ax_trajectories.set_xlim(0, experiment.config.simulation.grid_size)
        ax_trajectories.set_ylim(0, experiment.config.simulation.grid_size)
        ax_trajectories.set_aspect('equal')

        # Proper time comparison
        proper_times = [e['proper_time'] for e in snapshot.entity_states]
        gamma_effs = [e['gamma_eff_measured'] for e in snapshot.entity_states]
        ax_times.scatter(proper_times, gamma_effs, alpha=0.7)
        ax_times.set_xlabel('Proper Time (τ)')
        ax_times.set_ylabel('γ_eff')
        ax_times.set_title('Time Dilation')
        ax_times.grid(True, alpha=0.3)

        fig.suptitle(f'Experiment 51i (V9) - Tick {tick}', fontsize=14, fontweight='bold')

    anim = FuncAnimation(fig, update, frames=len(snapshots), interval=1000//fps, repeat=True)

    # Save animation
    writer = PillowWriter(fps=fps)
    anim.save(output_path, writer=writer)
    print(f"Animation saved: {output_path}")

    return anim


if __name__ == "__main__":
    # Demo: Show visualization capabilities
    print("=" * 70)
    print("VISUALIZATION MODULE - DEMO")
    print("=" * 70)
    print()

    print("This module provides comprehensive visualization tools:")
    print()
    print("Static Plots:")
    print("  - plot_gamma_field(): Time dilation heatmap")
    print("  - plot_load_energy_fields(): Load and energy fields")
    print("  - plot_entity_trajectories(): Entity paths through field")
    print("  - plot_gamma_vs_distance(): Gravitational gradient validation")
    print("  - plot_gamma_vs_velocity(): Lorentz factor validation")
    print("  - plot_summary_dashboard(): Comprehensive multi-panel view")
    print()
    print("Animated:")
    print("  - create_animation(): Full simulation evolution")
    print()
    print("Usage example:")
    print("""
    from visualize import plot_summary_dashboard, create_animation

    # After running experiment
    experiment = Experiment51i(config)
    experiment.run()

    # Create summary dashboard
    plot_summary_dashboard(
        experiment.mobile_entities,
        experiment.fields,
        planet_center=(50.0, 50.0),
        save_path='results/dashboard.png'
    )

    # Create animation
    create_animation(
        experiment,
        output_path='results/animation.gif',
        fps=10
    )
    """)
    print()
