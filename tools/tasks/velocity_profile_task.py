from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import math, particle_centers


@register_task(name="VelocityProfileTask")
class VelocityProfileTask(AbstractTask):
    """
    Task that computes radial velocity distribution. Algorithm: take the center and then
    draw a bunch of concentric sphere slices (number depends on `resolution`). For each slice
    compute average velocity module of the particles inside.

    Args:
    * `r_unit` (`ScalarQuantity`): unit of the radius for the output.
    * `v_unit` (`ScalarQuantity`): unit of the velocity for the output.
    * `resolution` (`int`): number of slices between nearest and farthest particle to the center.

    Dynamic args:
    * `center` (`VectorQuantity`): position of the center of profile. Center of mass by default.
    * `center_vel` (`VectorQuantity`): velocity of the center of profile.
    Center of mass velocity by default.

    Returns:
    * `radii`: list of radii of the sphere slices.
    * `velocity`: list of velocity modules for each slice.
    """

    def __init__(
        self,
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        v_unit: ScalarQuantity = 1 | units.kms,
    ) -> None:
        super().__init__()
        self.resolution = resolution
        self.r_unit = r_unit
        self.v_unit = v_unit

    @profiler("Velocity profile task")
    def run(
        self,
        snapshot: Snapshot,
        center: VectorQuantity | None = None,
        center_vel: VectorQuantity | None = None,
    ) -> DataType:
        if center is None:
            center = particle_centers.center_of_mass(snapshot.particles)
        if center_vel is None:
            center_vel = particle_centers.center_of_mass_velocity(snapshot.particles)

        particles = snapshot.particles

        radii = math.get_lengths(particles.position - center)
        velocities = math.get_lengths(particles.velocity - center_vel)
        radii, velocities = math.sort_with(radii, velocities)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution
        radii = radii[0 : number_of_chunks : self.resolution]
        velocities = velocities[:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        return {"radii": radii / self.r_unit, "velocity": velocities / self.v_unit}
