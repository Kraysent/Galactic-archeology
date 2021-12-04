import pyfalcon
from amuse.datamodel.particles import Particle, Particles
from amuse.lab import units
from amuse.units.quantities import ScalarQuantity
from omtool.datamodel import Snapshot


class PyfalconIntegrator:
    units_dict = {
        'L': units.kpc,
        'V': units.kms,
        'M': 232500 * units.MSun,
        'T': units.Gyr
    }

    def __init__(self, 
        snapshot: Snapshot,
        eps: ScalarQuantity,
        kmax: float
    ):
        self.pos, self.vel, self.mass, self.is_barion, self.time = self._get_params(snapshot)
        self.eps = eps.value_in(self.units_dict['L'])
        self.dt = 0.5 ** kmax
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)

    def _get_params(self, snapshot: Snapshot):
        pos = snapshot.particles.position.value_in(self.units_dict['L'])
        vel = snapshot.particles.velocity.value_in(self.units_dict['V'])
        mass = snapshot.particles.mass.value_in(self.units_dict['M'])
        is_barion = snapshot.particles.is_barion
        time = snapshot.timestamp.value_in(self.units_dict['T'])
        
        return (pos, vel, mass, is_barion, time)

    def leapfrog(self):
        self.vel += self.acc * (self.dt / 2)
        self.pos += self.vel * self.dt
        self.acc, _ = pyfalcon.gravity(self.pos, self.mass, self.eps)
        self.vel += self.acc * (self.dt / 2)
        self.time += self.dt

    @property
    def timestamp(self):
        return self.time | self.units_dict['T']

    def get_snapshot(self) -> Snapshot:
        N = len(self.mass)
        snapshot = Snapshot(Particles(N), self.time | units.Myr)
        pos = self.pos.reshape(N, -1, order = 'F') | self.units_dict['L']
        vel = self.vel.reshape(N, -1, order = 'F') | self.units_dict['V']
        mass = self.mass | self.units_dict['M']
        
        snapshot.particles.position = pos
        snapshot.particles.velocity = vel
        snapshot.particles.mass = mass
        snapshot.particles.is_barion = self.is_barion
        snapshot.timestamp = self.time | self.units_dict['T']

        return snapshot

    def get_particle(self, particle_id: int) -> Particle:
        particle = Particle()
        particle.position = self.pos[particle_id] | self.units_dict['L']
        particle.velocity = self.vel[particle_id] | self.units_dict['V']
        particle.mass = self.mass[particle_id] | self.units_dict['M']
        particle.is_barion = self.is_barion[particle_id]

        return particle