'''
Task that computes bound mass of the system.
'''
from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTimeTask
from omtool.analysis.utils import math, pyfalcon_analizer
from omtool.datamodel import Snapshot
from omtool.datamodel import profiler


def _get_bound_particles(particles):
    potentials = pyfalcon_analizer.get_potentials(particles, 0.2 | units.kpc)
    velocities = math.get_lengths(
        particles.velocity - particles.center_of_mass_velocity()
    )
    full_specific_energies = potentials + velocities ** 2 / 2

    return particles[full_specific_energies < (0 | units.J / units.MSun)]


class BoundMassTask(AbstractTimeTask):
    '''
    Task that computes bound mass of the system.
    '''

    def __init__(self, number_of_iterations: int = 3, change_threshold: float = 0.05):
        super().__init__()
        self.number_of_iterations = number_of_iterations
        self.change_threshold = change_threshold

    @profiler('Bound mass task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        bound_particles = snapshot.particles
        curr_len = len(bound_particles)
        prev_len = 0
        change = 1
        i = 0

        while change >= self.change_threshold:
            bound_particles = _get_bound_particles(bound_particles)
            prev_len = curr_len
            curr_len = len(bound_particles)

            if curr_len == 0 or prev_len == 0:
                break

            change = (prev_len - curr_len) / prev_len
            i += 1

            if i >= self.number_of_iterations:
                break

        self._append_value(
            snapshot, bound_particles.total_mass().value_in(units.MSun))

        return self._as_tuple()
