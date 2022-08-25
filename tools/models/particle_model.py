from amuse.lab import Particles, ScalarQuantity, units

from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="body")
class ParticleModel(AbstractModel):
    """
    Create snapshot from the single mass value at the origin.
    """

    def __init__(self, mass: ScalarQuantity):
        self.mass = mass

    def run(self) -> Snapshot:
        particles = Particles(1)
        particles[0].position = [0, 0, 0] | units.kpc
        particles[0].velocity = [0, 0, 0] | units.kms
        particles[0].mass = self.mass
        particles[0].is_barion = True

        return Snapshot(particles, 0 | units.Myr)
