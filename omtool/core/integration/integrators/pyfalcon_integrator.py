"""
Wrapper for pyfalcon module that connects it with AMUSE particle sets.
"""
import pyfalcon
from amuse.datamodel.particles import Particle, Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity

from omtool.core.datamodel import Snapshot


class PyfalconIntegrator:
    """
    Wrapper for pyfalcon module that connects it with AMUSE particle sets.
    """

    units_dict = {
        "L": units.kpc,
        "V": units.kms,
        "M": 232500 * units.MSun,
        "T": units.Gyr,
    }

    def __init__(self, snapshot: Snapshot, eps: ScalarQuantity, kmax: float):
        self.pos, self.vel, self.mass, self.is_barion, self.time = self._get_params(snapshot)
        self.eps = eps.value_in(self.units_dict["L"])
        self.delta_time = 0.5**kmax
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(self.units_dict["L"])
        vel = snapshot.particles.velocity.value_in(self.units_dict["V"])
        mass = snapshot.particles.mass.value_in(self.units_dict["M"])
        is_barion = snapshot.particles.is_barion
        time = snapshot.timestamp.value_in(self.units_dict["T"])

        return (pos, vel, mass, is_barion, time)

    def leapfrog(self):
        """
        Run one step of integration.
        """
        self.vel += self.acc * (self.delta_time / 2)
        self.pos += self.vel * self.delta_time
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.vel += self.acc * (self.delta_time / 2)
        self.time += self.delta_time

    @property
    def timestamp(self):
        """
        Obtain current timestamp.
        """
        return self.time | self.units_dict["T"]

    def get_snapshot(self) -> Snapshot:
        """
        Obtain current snaphot object.
        """
        number_of_particles = len(self.mass)
        snapshot = Snapshot(Particles(number_of_particles), self.time | units.Myr)
        pos = self.pos.reshape(number_of_particles, -1, order="F") | self.units_dict["L"]
        vel = self.vel.reshape(number_of_particles, -1, order="F") | self.units_dict["V"]
        mass = self.mass | self.units_dict["M"]

        snapshot.particles.position = pos
        snapshot.particles.velocity = vel
        snapshot.particles.mass = mass
        snapshot.particles.is_barion = self.is_barion
        snapshot.timestamp = self.time | self.units_dict["T"]

        return snapshot

    def get_particle(self, particle_id: int) -> Particle:
        """
        Obtain single particle from the simulation.
        """
        particle = Particle()
        particle.position = self.pos[particle_id] | self.units_dict["L"]
        particle.velocity = self.vel[particle_id] | self.units_dict["V"]
        particle.mass = self.mass[particle_id] | self.units_dict["M"]
        particle.is_barion = self.is_barion[particle_id]

        return particle
