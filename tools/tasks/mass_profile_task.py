"""
Task that computes radial distribution of cumulative mass.
"""
import numpy as np
from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import math, particle_centers


@register_task(name="MassProfileTask")
class MassProfileTask(AbstractTask):
    """
    Task that computes radial distribution of cumulative mass. Algorithm: take the center and then
    draw a bunch of concentric spheres (number depends on `resolution`). Count cumulitive
    mass in each sphere.

    Args:
    * `r_unit` (`ScalarQuantity`): unit of the radius for the output.
    * `m_unit` (`ScalarQuantity`): unit of the mass for the output.
    * `center_type` (`str`): id of the center type, e.g. center of mass of center of potential.
    * `resolution` (`int`): number of slices between nearest and farthest particle to the center.

    Returns:
    * `radii`: list of radii of the spheres.
    * `masses`: list of masses for each sphere.
    """

    def __init__(
        self,
        center_type: str = "mass",
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        m_unit: ScalarQuantity = 1 | units.MSun,
    ) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.resolution = resolution
        self.r_unit = r_unit
        self.m_unit = m_unit

    @profiler("Mass profile task")
    def run(self, snapshot: Snapshot) -> DataType:
        particles = snapshot.particles
        center = self.center_func(particles)

        radii = math.get_lengths(particles.position - center)
        masses = particles.mass
        radii, masses = math.sort_with(radii, masses)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0 : number_of_chunks : self.resolution]
        masses = masses[:number_of_chunks].reshape((-1, self.resolution)).sum(axis=1)
        masses = np.cumsum(masses)

        return {"radii": radii / self.r_unit, "masses": masses / self.m_unit}
