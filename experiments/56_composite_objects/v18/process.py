"""
V18 Process - Base class for unified composite processes.

Every entity in the V18 universe is a CompositeProcess:
- Has ONE imprint (unified spatial presence)
- Has ONE wake (∂gamma/∂t derivative)
- Has ONE tick_budget (shared energy)
- Has internal_state (encodes structure)

Examples:
- Photon: degenerate process (no internal structure)
- Hydrogen atom: proton + electron cloud (orbital state)
- H2 molecule: two protons + bonded electrons (molecular state)
- Complex molecule: many nuclei + electron density

Author: V18 Implementation
Date: 2026-02-04
Based on: RAW-083 Unified Imprint Principle
"""

from typing import Dict, Tuple, Optional, List
import numpy as np
from abc import ABC, abstractmethod

try:
    from .canvas_v18 import Canvas3D_V18, Pos3D
except ImportError:
    from canvas_v18 import Canvas3D_V18, Pos3D


class InternalState(ABC):
    """Base class for process internal structure.

    Different processes have different internal states encoding structure.
    """

    @abstractmethod
    def get_imprint_profile(self) -> Dict[Pos3D, float]:
        """Get imprint shape based on current state.

        Returns:
            {relative_pos: strength} relative to process center
        """
        pass

    @abstractmethod
    def transition(
        self,
        canvas: 'Canvas3D_V18',
        center: Pos3D,
        tick_budget: float,
    ) -> Tuple[bool, float]:
        """Compute next internal state.

        Args:
            canvas: Canvas with current gamma/wake fields
            center: Process center position
            tick_budget: Energy available this tick

        Returns:
            (continues, energy_used)
            - continues: True to continue, False if process expires
            - energy_used: How much of tick_budget was consumed
        """
        pass


class CompositeProcess(ABC):
    """Base class for unified composite processes.

    Properties:
    - ONE imprint (spatial presence)
    - ONE wake (∂gamma/∂t)
    - ONE tick_budget (shared energy)
    - internal_state (structure encoding)
    """

    def __init__(
        self,
        process_id: int,
        center: Pos3D,
        internal_state: InternalState,
        tick_budget: float = 1.0,
    ):
        """Initialize composite process.

        Args:
            process_id: Unique identifier
            center: Initial center position
            internal_state: Structure encoding
            tick_budget: Energy per tick
        """
        self.process_id = process_id
        self.center = center
        self.internal_state = internal_state
        self.tick_budget = tick_budget

        # History
        self.birth_tick = 0
        self.age_ticks = 0
        self.total_energy_spent = 0.0

        # Statistics
        self.acts_count = 0
        self.skips_count = 0
        self.imprint_strength_total = 0.0

    @property
    def time_dilation_factor(self) -> float:
        """Measure of how "slowed down" this process is.

        Caused by expansion resistance (gamma costs).

        Returns:
            acts / (acts + skips), or 1.0 if no experience
        """
        total = self.acts_count + self.skips_count
        if total == 0:
            return 1.0
        return self.acts_count / total

    def step(self, canvas: Canvas3D_V18) -> bool:
        """Execute one tick of this process.

        Args:
            canvas: Shared gamma field

        Returns:
            True if continues, False if expired
        """
        # 1. Read shared canvas state (gamma, wake)
        local_gamma = canvas.get_local_gamma_sum(self.center, radius=3)
        wake_grad = canvas.get_wake_gradient(self.center)

        # 2. Check expansion resistance (skip probability)
        # Higher gamma nearby = harder to act
        gamma_cost = canvas.get_effective_gamma(self.center, local_radius=3)
        skip_probability = gamma_cost * 0.1  # Physical constant

        if np.random.random() < skip_probability:
            self.skips_count += 1
            return True  # Continue even if skipped

        # 3. Execute internal state transition
        self.acts_count += 1
        continues, energy_used = self.internal_state.transition(
            canvas=canvas,
            center=self.center,
            tick_budget=self.tick_budget - self.total_energy_spent,
        )

        self.total_energy_spent += energy_used

        # 4. Paint unified imprint based on new internal state
        imprint_profile = self.internal_state.get_imprint_profile()
        canvas.paint_imprint(self.process_id, imprint_profile, self.center)

        # Track total imprint strength
        self.imprint_strength_total += sum(imprint_profile.values())

        # 5. Try to move (gradient-following)
        # Process moves toward higher gradient (toward other imprints)
        grad = canvas.get_gradient(self.center)
        grad_mag = np.sqrt(sum(g*g for g in grad))

        if grad_mag > 0.01:  # Only if significant gradient
            # Step toward gradient
            step = tuple(
                int(np.sign(g)) if g != 0 else 0
                for g in grad
            )
            self.center = tuple(c + s for c, s in zip(self.center, step))
        else:
            # Small random jitter when no gradient
            jitter = tuple(
                np.random.randint(-1, 2)
                for _ in range(3)
            )
            self.center = tuple(c + j for c, j in zip(self.center, jitter))

        self.age_ticks += 1

        return continues

    def get_statistics(self) -> Dict[str, any]:
        """Get process statistics.

        Returns:
            Dict with process state info
        """
        return {
            'process_id': self.process_id,
            'center': self.center,
            'age_ticks': self.age_ticks,
            'acts_count': self.acts_count,
            'skips_count': self.skips_count,
            'time_dilation_factor': self.time_dilation_factor,
            'imprint_strength_total': self.imprint_strength_total,
            'energy_spent': self.total_energy_spent,
        }


class SimpleDegenerateProcess(CompositeProcess):
    """Simplest possible process: photon or test particle.

    No internal structure - just paints single cell.
    Used for testing and baseline comparison.
    """

    class TrivialState(InternalState):
        """No internal structure."""

        def get_imprint_profile(self) -> Dict[Pos3D, float]:
            """Single cell imprint."""
            return {(0, 0, 0): 1.0}

        def transition(self, canvas, center, tick_budget) -> Tuple[bool, float]:
            """No state change."""
            return (True, 0.1)  # Consume minimal energy

    def __init__(self, process_id: int, center: Pos3D):
        """Initialize degenerate process."""
        super().__init__(
            process_id=process_id,
            center=center,
            internal_state=SimpleDegenerateProcess.TrivialState(),
            tick_budget=1.0,
        )
