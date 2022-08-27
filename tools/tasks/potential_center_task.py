from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import particle_centers


@register_task(name="PotentialCenterTask")
class PotentialCenterTask(AbstractTask):
    """
    Task that computes center of the particle system as a center of mass of certain fraction of
    particles with a smallest gravitational potential.

    Args:
    * `eps` (`ScalarQuanity`): softening distance for the potential algorithm.
    * `top_fraction` (`float`): center of mass of which fraction of top particles by potential
    to compute.

    Returns:
    * `position` (`VectorQuantity`): position of the particle center.
    * `velocity` (`VectorQuantity`): velocity of the particle center.
    """

    def __init__(self, eps: ScalarQuantity = 0.2 | units.kpc, top_fraction: float = 0.01):
        self.eps = eps
        self.top_fraction = top_fraction

    @profiler("Potential center task")
    def run(self, snapshot: Snapshot) -> DataType:
        position = particle_centers.potential_center(
            snapshot.particles, self.eps, self.top_fraction
        )
        velocity = particle_centers.potential_center_velocity(
            snapshot.particles, self.eps, self.top_fraction
        )

        return {"position": position, "velocity": velocity}
