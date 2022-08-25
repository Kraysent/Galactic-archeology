from amuse.ic.plummer import new_plummer_sphere
from amuse.lab import ScalarQuantity, nbody_system, units

from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="plummer_sphere")
class PlummerModel(AbstractModel):
    def __init__(self, number_of_particles: int, mass: ScalarQuantity, radius: ScalarQuantity):
        self.convert_nbody = nbody_system.nbody_to_si(mass, radius)
        self.number = number_of_particles
        self.radius = radius

    def run(self) -> Snapshot:
        particles = new_plummer_sphere(self.number, self.convert_nbody)
        particles.is_barion = [True] * len(particles)

        return Snapshot(particles, 0 | units.Myr)
