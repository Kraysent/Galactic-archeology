'''
Task that computes radial distribution of cumulative mass.
'''
from typing import Tuple

import numpy as np
from amuse.lab import units, ScalarQuantity
from omtool.core.analysis.tasks import AbstractTask
from omtool.core.analysis.utils import math, particle_centers
from omtool.core.datamodel import Snapshot, profiler


class MassProfileTask(AbstractTask):
    '''
    Task that computes radial distribution of cumulative mass.
    '''

    def __init__(
        self,
        center_type: str = 'mass',
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        m_unit: ScalarQuantity = 1 | units.MSun
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.m_unit = m_unit

    @profiler('Mass profile task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        center = self.center_func(particles)

        radii = math.get_lengths(particles.position - center)
        masses = particles.mass
        radii, masses = math.sort_with(radii, masses)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0:number_of_chunks:self.resolution]
        masses = masses[0:number_of_chunks].reshape((-1, self.resolution)).sum(axis=1)
        masses = np.cumsum(masses)

        return (radii / self.r_unit, masses / self.m_unit)
