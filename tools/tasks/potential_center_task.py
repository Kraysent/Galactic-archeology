from amuse.lab import ScalarQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import DataType, register_task
from tools.tasks.center_task import CenterTask


@register_task(name="PotentialCenterTask")
class PotentialCenterTask(CenterTask):
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
        super().__init__(center_type="potential", eps=eps, top_fraction=top_fraction)

    @profiler("Potential center task")
    def run(self, snapshot: Snapshot) -> DataType:
        return super().run(snapshot)
