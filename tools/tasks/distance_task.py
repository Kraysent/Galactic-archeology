"""
Task that computes distance between point and some specified position.
"""
from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTimeTask, DataType, register_task


@register_task(name="DistanceTask")
class DistanceTask(AbstractTimeTask):
    """
    Task that computes distance between two points or centers.

    Args:
    * `time_unit` (`ScalarQuantity`): unit of the time for the output.
    * `dist_unit` (`ScalarQuantity`): unit of the distance for the output.

    Dynamic args:
    * `start` (`VectorQuantity`): position of the start of distance vector.
    * `end` (`VectorQuantity`): position of the end of distance vector.

    Returns:
    * `times`: list of timestamps of snapshots.
    * `dist`: list of distances over time.
    """

    def __init__(
        self,
        time_unit: ScalarQuantity = 1 | units.Myr,
        dist_unit: ScalarQuantity = 1 | units.kpc,
    ):
        super().__init__(time_unit=time_unit, value_unit=dist_unit)

    @profiler("Distance task")
    def run(
        self,
        snapshot: Snapshot,
        start: VectorQuantity | None = None,
        end: VectorQuantity | None = None,
    ) -> DataType:
        if start is None:
            raise RuntimeError("DistanceTask.start is not defined")

        if end is None:
            raise RuntimeError("DistanceTask.end is not defined")

        dist = (end - start).length()
        self._append_value(snapshot, dist)
        result = self._as_tuple()
        return {"times": result[0], "dist": result[1]}
