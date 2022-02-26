from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTimeTask
from omtool.analysis.utils import math, pyfalcon_analizer
from omtool.datamodel import Snapshot
from omtool.datamodel import profiler


class BoundMassTask(AbstractTimeTask):
    def __init__(self, number_of_iterations: int = 3):
        super().__init__()
        self.number_of_iterations = number_of_iterations

    def _get_bound_particles(self, particles):
        potentials = pyfalcon_analizer.get_potentials(particles, 0.2 | units.kpc)
        velocities = math.get_lengths(particles.velocity - particles.center_of_mass_velocity())
        full_specific_energies = potentials + velocities ** 2 / 2

        return particles[full_specific_energies < (0 | units.J / units.MSun)]

    @profiler('Bound mass task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        bound_particles = snapshot.particles

        for i in range(self.number_of_iterations):
            bound_particles = self._get_bound_particles(bound_particles)

        self._append_value(snapshot, bound_particles.total_mass().value_in(units.MSun))

        return self._as_tuple()
