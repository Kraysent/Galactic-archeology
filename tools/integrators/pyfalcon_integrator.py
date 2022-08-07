import pyfalcon
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from omtool.core.datamodel import AbstractIntegrator, Snapshot
from omtool.core.integrators import register_integrator


@register_integrator(name="pyfalcon")
class PyfalconIntegrator(AbstractIntegrator):
    """
    Wrapper for pyfalcon module that connects it with AMUSE particle sets.
    """

    units_dict = {
        "L": units.kpc,
        "V": units.kms,
        "M": 232500 * units.MSun,
        "T": units.Gyr,
    }

    def __init__(self, eps: ScalarQuantity, kmax: float):
        self.eps = eps.value_in(self.units_dict["L"])
        self.delta_time = 0.5**kmax

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(self.units_dict["L"])
        vel = snapshot.particles.velocity.value_in(self.units_dict["V"])
        mass = snapshot.particles.mass.value_in(self.units_dict["M"])
        is_barion = snapshot.particles.is_barion
        time = snapshot.timestamp.value_in(self.units_dict["T"])

        return (pos, vel, mass, is_barion, time)

    def leapfrog(self, snapshot: Snapshot) -> Snapshot:
        """
        Run one step of integration.
        """
        pos, vel, mass, is_barion, time = self._get_params(snapshot)
        if not hasattr(self, "acc"):
            self.acc, _ = pyfalcon.gravity(pos, mass, self.eps)

        vel += self.acc * (self.delta_time / 2)
        pos += vel * self.delta_time
        self.acc, _ = pyfalcon.gravity(pos, mass, self.eps)
        vel += self.acc * (self.delta_time / 2)
        time += self.delta_time

        number_of_particles = len(mass)
        new_snapshot = Snapshot(Particles(number_of_particles), time | units.Myr)
        pos = pos.reshape(number_of_particles, -1, order="F") | self.units_dict["L"]
        vel = vel.reshape(number_of_particles, -1, order="F") | self.units_dict["V"]
        mass = mass | self.units_dict["M"]

        new_snapshot.particles.position = pos
        new_snapshot.particles.velocity = vel
        new_snapshot.particles.mass = mass
        new_snapshot.particles.is_barion = is_barion
        new_snapshot.timestamp = time | self.units_dict["T"]

        return new_snapshot
