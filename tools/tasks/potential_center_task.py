from omtool.core.datamodel import Snapshot
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import particle_centers


@register_task(name="PotentialCenterTask")
class PotentialCenterTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> DataType:
        position = particle_centers.potential_center(snapshot.particles)
        velocity = particle_centers.potential_center_velocity(snapshot.particles)

        return {"position": position, "velocity": velocity}
