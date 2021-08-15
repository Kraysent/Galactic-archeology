from amuse.datamodel.particles import Particles
from amuse.units.quantities import ScalarQuantity


class Snapshot:
    def __init__(self, particles: Particles, timestamp: ScalarQuantity):
        self.particles = particles
        self.timestamp = timestamp

    def __getitem__(self, value) -> 'Snapshot':
        return Snapshot(self.particles[value], self.timestamp)

    def __add__(self, other: 'Snapshot') -> 'Snapshot':
        if self.timestamp == other.timestamp:
            particles = Particles()
            particles.add_particles(self.particles)
            particles.add_particles(other.particles)

            return Snapshot(particles, self.timestamp)
        else:
            raise RuntimeError('Tried to sum snapshots with different timestamps.')
