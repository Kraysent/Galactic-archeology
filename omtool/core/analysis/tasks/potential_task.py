'''
Task that computes radial distribution of the potential.
'''
from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.core.analysis.tasks import AbstractTask
from omtool.core.analysis.utils import math, particle_centers, pyfalcon_analizer
from omtool.core.datamodel import Snapshot, profiler


class PotentialTask(AbstractTask):
    '''
    Task that computes radial distribution of the potential.
    '''

    def __init__(self, center_type: str = 'mass', resolution: int = 1000) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution

    @profiler('Potential task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        center = self.center_func(snapshot.particles)
        particles = snapshot.particles

        r = math.get_lengths(particles.position - center)
        potentials = pyfalcon_analizer.get_potentials(
            snapshot.particles, 0.2 | units.kpc)
        (r, potentials) = math.sort_with(r, potentials)

        number_of_chunks = (len(r) // self.resolution) * self.resolution

        r = r[0:number_of_chunks:self.resolution]
        potentials = potentials[0:number_of_chunks].reshape(
            (-1, self.resolution)).mean(axis=1)
        potentials = potentials / potentials.mean()

        return (r.value_in(units.kpc), potentials)
