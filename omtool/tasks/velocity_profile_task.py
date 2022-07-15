"""
Task that computes radial velocity distribution.
"""
from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import (
    AbstractTask,
    DataType,
    Snapshot,
    filter_barion_particles,
    profiler,
)
from omtool.core.utils import math, particle_centers


class VelocityProfileTask(AbstractTask):
    """
    Task that computes radial velocity distribution.
    """

    def __init__(
        self,
        center_type: str = "mass",
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        v_unit: ScalarQuantity = 1 | units.kms,
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.center_vel_func = particle_centers.get_velocity(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.v_unit = v_unit

    @profiler("Velocity profile task")
    def run(self, snapshot: Snapshot) -> DataType:
        center = self.center_func(snapshot.particles)
        center_vel = self.center_vel_func(snapshot.particles)

        particles = filter_barion_particles(snapshot)

        radii = math.get_lengths(particles.position - center)
        velocities = math.get_lengths(particles.velocity - center_vel)
        radii, velocities = math.sort_with(radii, velocities)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution
        radii = radii[0 : number_of_chunks : self.resolution]
        velocities = velocities[0:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        return {"radii": radii / self.r_unit, "velocity": velocities / self.v_unit}
