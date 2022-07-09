"""
Task that computes radial distribution of the potential.
"""
from typing import Tuple

import numpy as np
from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import AbstractTask, Snapshot, profiler, DataType
from omtool.core.utils import math, particle_centers, pyfalcon_analizer


class PotentialTask(AbstractTask):
    """
    Task that computes radial distribution of the potential.
    """

    def __init__(
        self,
        center_type: str = "mass",
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        pot_unit: ScalarQuantity = None,
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.pot_unit = pot_unit

    @profiler("Potential task")
    def run(self, snapshot: Snapshot) -> DataType:
        center = self.center_func(snapshot.particles)
        particles = snapshot.particles

        radii = math.get_lengths(particles.position - center)
        potentials = pyfalcon_analizer.get_potentials(snapshot.particles, 0.2 | units.kpc)
        radii, potentials = math.sort_with(radii, potentials)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0 : number_of_chunks : self.resolution]
        potentials = potentials[0:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        if self.pot_unit is None:
            self.pot_unit = potentials.mean()

        return {"radii": radii / self.r_unit, "potential": potentials / self.pot_unit}
