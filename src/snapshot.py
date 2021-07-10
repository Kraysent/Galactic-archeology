from amuse.datamodel.particles import Particles
from amuse.units.quantities import ScalarQuantity

class Snapshot:
    def __init__(self, particles: Particles, timestamp: ScalarQuantity) -> None:
        self.particles = particles
        self.timestamp = timestamp