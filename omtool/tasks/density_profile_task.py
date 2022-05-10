"""
Task that computes radial distribution of density.
"""
from typing import Tuple

import numpy as np
from amuse.lab import units, ScalarQuantity
from omtool.tasks import AbstractTask
from omtool.core.analysis.utils import math, particle_centers
from omtool.core.datamodel import Snapshot, profiler


class DensityProfileTask(AbstractTask):
    """
    Task that computes radial distribution of density.
    """

    def __init__(
        self,
        center_type: str = "mass",
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        dens_unit: ScalarQuantity = 1 | units.MSun / units.kpc**3,
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.dens_unit = dens_unit

    @profiler("Density profile task")
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        center = self.center_func(particles)

        radii = math.get_lengths(particles.position - center)
        masses = particles.mass
        radii, masses = math.sort_with(radii, masses)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0 : number_of_chunks : self.resolution]
        masses = (
            masses[0:number_of_chunks]
            .reshape(shape=(-1, self.resolution))
            .sum(axis=1)[1:]
        )
        volume = 4 / 3 * np.pi * (radii[1:] ** 3 - radii[:-1] ** 3)
        densities = masses / volume
        radii = radii[1:]

        return (radii / self.r_unit, densities / self.dens_unit)
