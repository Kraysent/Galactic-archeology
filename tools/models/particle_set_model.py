from pprint import pprint
import numpy as np
from amuse.lab import Particles, ScalarQuantity, units

from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="set")
class ParticleSetModel(AbstractModel):
    """
    Create snapshot with a number of particles of equal mass with random velocities and positions
    in a given range.
    """

    def __init__(
        self,
        number_of_particles: int,
        total_mass: ScalarQuantity,
        velocity_std: ScalarQuantity,
        x_width: ScalarQuantity,
        y_width: ScalarQuantity,
        z_width: ScalarQuantity,
    ):
        self.N = number_of_particles
        self.mass = total_mass
        self.velocity_std = velocity_std
        self.dimentions = (x_width, y_width, z_width)

    def run(self) -> Snapshot:
        if self.N == 0:
            return Snapshot()

        center = 0
        std_dev = self.velocity_std.value_in(units.kms)
        velocity_set = np.random.normal(center, std_dev, (self.N, 3)) | units.kms
        dimentions = [dim.value_in(units.kpc) for dim in self.dimentions]
        x_set = np.random.uniform(-dimentions[0] / 2, dimentions[0] / 2, self.N) | units.kpc
        y_set = np.random.uniform(-dimentions[1] / 2, dimentions[1] / 2, self.N) | units.kpc
        z_set = np.random.uniform(-dimentions[2] / 2, dimentions[2] / 2, self.N) | units.kpc

        snapshot = Snapshot(Particles(self.N))
        snapshot.particles.velocity = velocity_set
        snapshot.particles.x = x_set
        snapshot.particles.y = y_set
        snapshot.particles.z = z_set

        snapshot.particles.mass = [self.mass / self.N] * self.N

        return snapshot
