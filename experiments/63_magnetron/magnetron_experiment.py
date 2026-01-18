from core.fields import GammaField
from core.patterns import Particle
from core.composites import CompositeBindingManager
from core.collision import CollisionManager
from core.utils import radial_gamma, anisotropy_gamma

class MagnetronExperiment:
    def __init__(self, cfg):
        self.cfg = cfg

        # --- Grid + gamma field ---
        self.gamma = GammaField(cfg.grid_size)

        # --- Geometry ---
        self.cathode_mask, self.anode_mask, self.cavity_mask = build_magnetron_geometry(cfg)

        # --- Managers ---
        self.collision = CollisionManager()
        self.composites = CompositeBindingManager()

        # --- Particles ---
        self.electrons = emit_electrons(cfg, self.cathode_mask)

    def step(self):
        # 1. Update gamma field
        self.gamma.clear_sources()
        self.gamma.add_static_source(self.cathode_mask, strength=cfg.cathode_strength)
        self.gamma.add_static_source(self.anode_mask, strength=cfg.anode_strength)

        # Add electrons as dynamic sources
        for e in self.electrons:
            self.gamma.add_point_source(e.pos, e.energy)

        # Apply radial gradient (E-field analog)
        self.gamma.apply(radial_gamma(self.cfg))

        # Apply anisotropy (B-field analog)
        self.gamma.apply(anisotropy_gamma(self.cfg))

        # Relax field
        self.gamma.relax(self.cfg.gamma_relax_steps)

        # 2. Move electrons in gamma geometry
        for e in self.electrons:
            grad = self.gamma.gradient_at(e.pos)
            e.update_velocity(grad, anisotropy=self.cfg.gamma_anisotropy)
            e.update_position()

        # 3. Collision + absorption
        self.electrons = [
            e for e in self.electrons
            if not hit_anode(e.pos, self.anode_mask)
        ]

        # 4. Measure cavity mode
        cavity_amp = measure_cavity_mode(self.gamma, self.cavity_mask)

        return cavity_amp
