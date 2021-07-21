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
            return Snapshot(self.particles + other.particles, self.timestamp)
        else:
            raise RuntimeError('Tried to sum snapshots with different timestamps.')