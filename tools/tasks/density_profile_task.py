"""
Task that computes radial distribution of density.
"""
import numpy as np
from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import math, particle_centers


@register_task(name="DensityProfileTask")
class DensityProfileTask(AbstractTask):
    """
    Task that computes radial distribution of density. Algorithm: take the center and then
    draw a bunch of concentric sphere slices (number depends on `resolution`). Count cumulitive
    mass in each sphere slice and divide it by the volume of it.

    Args:
    * `r_unit` (`ScalarQuantity`): unit of the radius for the output.
    * `dens_unit` (`ScalarQuantity`): unit of the density for the output.
    * `resolution` (`int`): number of slices between nearest and farthest particle to the center.

    Dynamic args:
    * `center` (`VectorQuantity`): position of the center of profile. Center of mass by default.

    Returns:
    * `radii`: list of radii of the sphere slices.
    * `densities`: list of densities for each slice.
    """

    def __init__(
        self,
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        dens_unit: ScalarQuantity = 1 | units.MSun / units.kpc**3,
    ) -> None:
        super().__init__()
        self.resolution = resolution
        self.r_unit = r_unit
        self.dens_unit = dens_unit

    @profiler("Density profile task")
    def run(
        self,
        snapshot: Snapshot,
        center: VectorQuantity | None = None,
    ) -> DataType:
        particles = snapshot.particles

        if center is None:
            center = particle_centers.center_of_mass(particles)

        radii = math.get_lengths(particles.position - center)
        masses = particles.mass
        radii, masses = math.sort_with(radii, masses)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0 : number_of_chunks : self.resolution]
        masses = masses[:number_of_chunks].reshape(shape=(-1, self.resolution)).sum(axis=1)[1:]
        volume = 4 / 3 * np.pi * (radii[1:] ** 3 - radii[:-1] ** 3)
        densities = masses / volume
        radii = radii[1:]

        return {"radii": radii / self.r_unit, "densities": densities / self.dens_unit}
