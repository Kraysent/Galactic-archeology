import pyfalcon
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity
from archeology.datamodel import Snapshot


class PyfalconIntegrator:
    def __init__(self, 
        snapshot: Snapshot,
        eps: ScalarQuantity,
        kmax: float
    ):
        self.pos, self.vel, self.mass, self.time = self._get_params(snapshot)
        self.eps = eps.value_in(units.kpc)
        self.dt = 0.5 ** kmax
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(units.kpc)
        vel = snapshot.particles.velocity.value_in(units.kms)
        mass = snapshot.particles.mass.value_in(232500 * units.MSun)
        time = snapshot.timestamp.value_in(units.Gyr)
        
        return (pos, vel, mass, time)

    def leapfrog(self):
        self.vel += self.acc * (self.dt / 2)
        self.pos += self.vel * self.dt
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.vel += self.acc * (self.dt / 2)
        self.time += self.dt

    def get_snapshot(self) -> Snapshot:
        N = len(self.mass)
        snapshot = Snapshot(Particles(N), self.time | units.Myr)
        pos = self.pos.reshape(N, -1, order = 'F') | units.kpc
        vel = self.vel.reshape(N, -1, order = 'F') | units.kms
        mass = self.mass | 232500 * units.MSun
        snapshot.particles.position = pos
        snapshot.particles.velocity = vel
        snapshot.particles.mass = mass
        snapshot.timestamp = self.time | units.Gyr

        return snapshot
