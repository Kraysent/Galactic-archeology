'''
Task that computes radial distribution of the potential.
'''
from typing import Tuple

import numpy as np
from amuse.lab import units, ScalarQuantity
from omtool.core.analysis.tasks import AbstractTask
from omtool.core.analysis.utils import math, particle_centers, pyfalcon_analizer
from omtool.core.datamodel import Snapshot, profiler


class PotentialTask(AbstractTask):
    '''
    Task that computes radial distribution of the potential.
    '''

    def __init__(
        self,
        center_type: str = 'mass',
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        pot_unit: ScalarQuantity = None
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.pot_unit = pot_unit

    @profiler('Potential task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        center = self.center_func(snapshot.particles)
        particles = snapshot.particles

        radii = math.get_lengths(particles.position - center)
        potentials = pyfalcon_analizer.get_potentials(snapshot.particles, 0.2 | units.kpc)
        radii, potentials = math.sort_with(radii, potentials)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0:number_of_chunks:self.resolution]
        potentials = potentials[0:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        if self.pot_unit is None:
            self.pot_unit = potentials.mean()

        return (radii / self.r_unit, potentials / self.pot_unit)
