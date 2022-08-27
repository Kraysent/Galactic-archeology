"""
Task that computes distance between point and some specified position.
"""
from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTimeTask, DataType, register_task
from omtool.core.utils import particle_centers


@register_task(name="DistanceTask")
class DistanceTask(AbstractTimeTask):
    """
    Task that computes distance between two points or centers.

    Args:
    * `time_unit` (`ScalarQuantity`): unit of the time for the output.
    * `dist_unit` (`ScalarQuantity`): unit of the distance for the output.
    * `start` (`int` | `str`): either index of the first particle or the id of the center.
    * `start_slice` (`slice`): if `start` is the center id, this is the slice over which this
    center is counted.
    * `end` (`int` | `str`): either index of the second particle or the id of the center.
    * `end_slice` (`slice`): if `end` is the center id, this is the slice over which this
    center is counted.

    Returns:
    * `times`: list of timestamps of snapshots.
    * `dist`: list of distances over time.
    """

    def __init__(
        self,
        time_unit: ScalarQuantity = 1 | units.Myr,
        dist_unit: ScalarQuantity = 1 | units.kpc,
        start: int | str | None = None,
        start_slice: slice = slice(0, None),
        end: int | str | None = None,
        end_slice: slice = slice(0, None),
    ):
        if start is not None:
            self.start_slice = start_slice

            if isinstance(start, int):
                self.start_id = start
            elif isinstance(start, str):
                self.start = particle_centers.get(start)
            else:
                raise ValueError(f"DistanceTask.start has incompatible type {type(start)}")

        if end is not None:
            self.end_slice = end_slice

            if isinstance(end, int):
                self.end_id = end
            elif isinstance(end, str):
                self.end = particle_centers.get(end)
            else:
                raise ValueError(f"DistanceTask.end has incompatible type {type(end)}")

        super().__init__(time_unit=time_unit, value_unit=dist_unit)

    @profiler("Distance task")
    def run(
        self,
        snapshot: Snapshot,
        start: VectorQuantity | None = None,
        end: VectorQuantity | None = None,
    ) -> DataType:
        if start is not None:
            start_pos = start
        elif hasattr(self, "start"):
            start_pos = self.start(snapshot[self.start_slice].particles)
        elif hasattr(self, "start_id"):
            start_pos = snapshot[self.start_slice].particles[self.start_id].position
        else:
            raise RuntimeError("DistanceTask.start or DistanceTask.start_id are not defined")

        if end is not None:
            end_pos = end
        elif hasattr(self, "end"):
            end_pos = self.end(snapshot[self.end_slice].particles)
        elif hasattr(self, "end_id"):
            end_pos = snapshot[self.end_slice].particles[self.end_id].position
        else:
            raise RuntimeError("DistanceTask.end or DistanceTask.end_id are not defined")

        dist = (end_pos - start_pos).length()
        self._append_value(snapshot, dist)
        result = self._as_tuple()
        return {"times": result[0], "dist": result[1]}


task = DistanceTask
