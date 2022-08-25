from amuse.lab import ScalarQuantity

from omtool.core.datamodel import Snapshot
from omtool.core.integrators import AbstractIntegrator, register_integrator


@register_integrator(name="dummy")
class DummyIntegrator(AbstractIntegrator):
    """
    This is dummy integrator. It should only be used for development of core module
    and is subject to change.

    Propogates each particle of the snapshot along the velocity vector.

    Args:
    * `timestep` (`ScalarQuantity`): timestep of the iteration.
    """

    def __init__(self, timestep: ScalarQuantity) -> None:
        self.timestep = timestep

    def leapfrog(self, snapshot: Snapshot) -> Snapshot:
        snapshot.particles.position += snapshot.particles.velocity * self.timestep
        snapshot.timestamp += self.timestep

        return snapshot
