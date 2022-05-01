'''
Task that computes radial distribution of density.
'''
from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.core.analysis.tasks import AbstractTask
from omtool.core.analysis.utils import math, particle_centers
from omtool.core.datamodel import Snapshot, profiler


class DensityProfileTask(AbstractTask):
    '''
    Task that computes radial distribution of density.
    '''

    def __init__(self, center_type: str = 'mass', resolution: int = 1000) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution

    @profiler('Density profile task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        center = self.center_func(particles)

        r = math.get_lengths(particles.position - center)
        m = particles.mass
        (r, m) = math.sort_with(r, m)

        number_of_chunks = (len(r) // self.resolution) * self.resolution

        r = r[0:number_of_chunks:self.resolution]
        m = m[0:number_of_chunks].reshape(shape=(-1, self.resolution)).sum(axis=1)[1:]
        volume = 4/3 * np.pi * (r[1:] ** 3 - r[:-1] ** 3)
        densities = m / volume
        r = r[1:]

        return (r.value_in(units.kpc), densities.value_in(units.MSun / units.kpc ** 3))
