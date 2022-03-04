from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTask
from omtool.analysis.utils import math, particle_centers, pyfalcon_analizer
from omtool.datamodel import Snapshot, profiler


class PotentialTask(AbstractTask):
    def __init__(self, center_type: str = 'mass') -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)

    @profiler('Potential task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        center = self.center_func(snapshot.particles)
        particles = snapshot.particles

        r = math.get_lengths(particles.position - center)
        potentials = pyfalcon_analizer.get_potentials(snapshot.particles, 0.2 | units.kpc)
        (r, potentials) = math.sort_with(r, potentials)

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution

        r = r[0:number_of_chunks:resolution]
        potentials = potentials[0:number_of_chunks].reshape((-1, resolution)).mean(axis = 1)
        potentials = potentials / potentials.mean()

        return (r.value_in(units.kpc), potentials)
