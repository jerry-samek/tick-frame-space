"""
V17 Renderer - Deterministic entity that paints on the canvas.

Ontologické principy V17:
1. Renderer je temporální proces, ne částice
2. Jediná paměť je canvas (gamma pole)
3. last_paint_pos je lokální rámec, ne identita
4. Vše je deterministické – žádný random, žádná pravděpodobnost

Chování:
- Gradient táhne renderer k vyšší gammě (jako gravitace)
- Skip je deterministická reakce na příliš velký gradient (stres)
- Když je gradient nenulový: krok po gradientu
- Když je gradient nulový, ale gamma>0: deterministický „tlak ven“
- Když je gradient nulový a gamma=0: zůstaň na místě
"""

import numpy as np
from typing import Tuple, Optional

try:
    from .canvas import Canvas3D, Pos3D
except ImportError:
    from canvas import Canvas3D, Pos3D


class Renderer:
    """Deterministický renderer – rozhoduje, kde malovat na základě canvasu."""

    def __init__(self, entity_id: int, seed: int):
        """Inicializace rendereru.

        entity_id a seed necháváme kvůli kompatibilitě,
        RNG ale v deterministické verzi nepoužíváme.
        """
        self.entity_id = entity_id
        self.rng = np.random.default_rng(seed + entity_id * 1000)

        # Lokální referenční bod – kde jsme naposledy malovali
        self.last_paint_pos: Pos3D = (0, 0, 0)

        # Statistika
        self.total_skips: int = 0
        self.total_acts: int = 0
        self.skip_accumulator: int = 0

    @property
    def time_dilation_factor(self) -> float:
        """Time dilation = acts / (acts + skips)."""
        total = self.total_acts + self.total_skips
        if total == 0:
            return 1.0
        return self.total_acts / total

    def render_tick(
            self,
            canvas: Canvas3D,
            skip_sensitivity: float = 0.01,
            jitter_strength: float = 0.1,
            gradient_threshold: float = 0.01,
            gamma_imprint: float = 1.0
    ) -> Optional[Pos3D]:
        """Deterministické rozhodnutí, kde malovat v tomto ticku.

        Args:
            canvas: aktuální canvas
            skip_sensitivity: fyzikální konstanta pro reakci na gradient (stres)
            jitter_strength: ignorováno (kvůli signatuře)
            gradient_threshold: ignorováno (kvůli signatuře)
            gamma_imprint: kolik gammy přidáme při malování

        Returns:
            Nová pozice, nebo None pokud byl tick přeskočen.
        """

        # 1) Gradient v aktuálním lokálním rámci
        gx, gy, gz = canvas.get_gradient(self.last_paint_pos)
        gradient_mag = np.sqrt(gx * gx + gy * gy + gz * gz)

        # 2) Lokální gamma – kolik „materiálu“ je pod námi
        gamma_here = canvas.get_gamma(self.last_paint_pos)

        # 3) Deterministický skip: příliš velký gradient → zamrznutí (dilatace)
        #    ŽÁDNÁ pravděpodobnost, čistá funkce gradientu.
        if gradient_mag * skip_sensitivity >= 1.0:
            self.total_skips += 1
            self.skip_accumulator += 1
            return None

        # 4) Renderer jedná v tomto ticku
        self.total_acts += 1
        self.skip_accumulator = 0

        # 5) Pohyb – tři režimy:

        if gradient_mag > 0.0:
            # a) Klasika: jdu po gradientu (k vyšší gammě)
            step = (
                int(np.sign(gx)) if gx != 0 else 0,
                int(np.sign(gy)) if gy != 0 else 0,
                int(np.sign(gz)) if gz != 0 else 0,
            )

        elif gamma_here > 0.0:
            # b) Sedím na hromadě gammy, ale gradient je plochý
            #    → deterministicky „tlačím ven“ – rozbití symetrie bez randomu.
            #    Nejjednodušší pravidlo: vždy krok v +x.
            step = (1, 0, 0)

        else:
            # c) Prázdnota a žádný gradient → zůstaň na místě
            step = (0, 0, 0)

        new_pos = (
            self.last_paint_pos[0] + step[0],
            self.last_paint_pos[1] + step[1],
            self.last_paint_pos[2] + step[2],
        )

        # 6) Malování na canvas
        canvas.paint(new_pos, gamma_imprint)

        # 7) Aktualizace lokálního rámce
        self.last_paint_pos = new_pos

        return new_pos

    def _sample_small_jitter(self, strength: float) -> Tuple[int, int, int]:
        """Zachováno kvůli signatuře, v deterministické verzi se nepoužívá."""
        return (0, 0, 0)

    def set_position(self, pos: Pos3D):
        """Nastaví aktuální lokální rámec (např. při inicializaci)."""
        self.last_paint_pos = pos

    def get_statistics(self) -> dict:
        """Statistiky rendereru."""
        return {
            "entity_id": self.entity_id,
            "position": self.last_paint_pos,
            "total_acts": self.total_acts,
            "total_skips": self.total_skips,
            "time_dilation": self.time_dilation_factor,
        }

    def __repr__(self) -> str:
        return (
            f"Renderer(id={self.entity_id}, "
            f"pos={self.last_paint_pos}, "
            f"dilation={self.time_dilation_factor:.2f})"
        )


if __name__ == "__main__":
    print("V17 Renderer Demo")
    print("=" * 70)

    canvas = Canvas3D()
    renderer = Renderer(entity_id=1, seed=42)

    print(f"Created: {renderer}\n")
    print("Simulating 20 ticks...")
    print("-" * 40)

    for tick in range(1, 21):
        result = renderer.render_tick(
            canvas,
            skip_sensitivity=0.01,
            jitter_strength=0.1,
            gradient_threshold=0.01,
            gamma_imprint=1.0,
        )
        if result is None:
            print(f"  Tick {tick:2d}: SKIPPED")
        else:
            print(f"  Tick {tick:2d}: painted at {result}")

    print()
    print(f"Final state: {renderer}\n")

    print("Canvas statistics:")
    stats = canvas.get_statistics()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print()
