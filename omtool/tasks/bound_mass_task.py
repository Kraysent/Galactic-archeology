"""
Task that computes bound mass of the system.
"""
from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import AbstractTimeTask, DataType, Snapshot, profiler
from omtool.core.utils import math, pyfalcon_analizer


def _get_bound_particles(particles):
    potentials = pyfalcon_analizer.get_potentials(particles, 0.2 | units.kpc)
    velocities = math.get_lengths(particles.velocity - particles.center_of_mass_velocity())
    full_specific_energies = potentials + velocities**2 / 2

    return particles[full_specific_energies < (0 | units.J / units.MSun)]


class BoundMassTask(AbstractTimeTask):
    """
    Task that computes bound mass of the system.
    """

    def __init__(
        self,
        time_unit: ScalarQuantity = 1 | units.Myr,
        mass_unit: ScalarQuantity = 1 | units.MSun,
        number_of_iterations: int = 3,
        change_threshold: float = 0.05,
    ):
        self.number_of_iterations = number_of_iterations
        self.change_threshold = change_threshold

        super().__init__(time_unit=time_unit, value_unit=mass_unit)

    @profiler("Bound mass task")
    def run(self, snapshot: Snapshot) -> DataType:
        bound_particles = snapshot.particles
        curr_len = len(bound_particles)
        prev_len = 0
        change = 1.0
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

        self._append_value(snapshot, bound_particles.total_mass())
        result = self._as_tuple()

        return {"times": result[0], "bound_mass": result[1]}
