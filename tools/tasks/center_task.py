from zlog import logger

from omtool.core.datamodel import Snapshot
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import particle_centers


@register_task(name="CenterTask")
class CenterTask(AbstractTask):
    """
    Task that computes center of the particle system from the specified function.

    Args:
    * `center_type` (`str`): type of the center (`mass`, `potential`).
    * `**kwargs`: keywoard arguments for the center from the `center_type` constructor.

    Returns:
    * `position` (`VectorQuantity`): position of the particle center.
    * `velocity` (`VectorQuantity`): velocity of the particle center.
    """

    def __init__(self, center_type: str = "mass", **kwargs):
        self.kwargs = kwargs

        if center_type == "mass":
            self.position_func = particle_centers.center_of_mass
            self.velocity_func = particle_centers.center_of_mass_velocity
        elif center_type == "potential":
            self.position_func = particle_centers.potential_center
            self.velocity_func = particle_centers.potential_center_velocity
        else:
            (
                logger.warn()
                .string("name", center_type)
                .msg("unknown center type, falling back to center of mass")
            )
            self.position_func = particle_centers.center_of_mass
            self.velocity_func = particle_centers.center_of_mass_velocity

    def run(self, snapshot: Snapshot) -> DataType:
        return {
            "position": self.position_func(snapshot.particles, **self.kwargs),
            "velocity": self.velocity_func(snapshot.particles, **self.kwargs),
        }
