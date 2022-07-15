"""
Task that computes distance between point and some specified position.
"""
from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import AbstractTimeTask, Snapshot, profiler, DataType
from omtool.core.utils import particle_centers


class DistanceTask(AbstractTimeTask):
    """
    Task that computes distance between point and some specified position.
    """

    def __init__(
        self,
        time_unit: ScalarQuantity = 1 | units.Myr,
        dist_unit: ScalarQuantity = 1 | units.kpc,
        start: int | str = "",
        start_slice: slice = slice(0, None),
        end: int | str = "",
        end_slice: slice = slice(0, None),
    ):
        self.start_slice = start_slice

        if isinstance(start, int):
            self.start_id = start
        elif isinstance(start, str):
            self.start = particle_centers.get(start)
        else:
            raise ValueError(f"DistanceTask.start has incompatible type {type(start)}")

        self.end_slice = end_slice

        if isinstance(end, int):
            self.end_id = end
        elif isinstance(end, str):
            self.end = particle_centers.get(end)
        else:
            raise ValueError(f"DistanceTask.end has incompatible type {type(end)}")

        super().__init__(time_unit=time_unit, value_unit=dist_unit)

    @profiler("Distance task")
    def run(self, snapshot: Snapshot) -> DataType:
        if hasattr(self, "start"):
            start_pos = self.start(snapshot[self.start_slice].particles)
        elif hasattr(self, "start_id"):
            start_pos = snapshot[self.start_slice].particles[self.start_id].position
        else:
            raise RuntimeError(f"DistanceTask.start or DistanceTask.start_id are not defined")

        if hasattr(self, "end"):
            end_pos = self.end(snapshot[self.end_slice].particles)
        elif hasattr(self, "end_id"):
            end_pos = snapshot[self.end_slice].particles[self.end_id].position
        else:
            raise RuntimeError(f"DistanceTask.end or DistanceTask.end_id are not defined")

        dist = (end_pos - start_pos).length()
        self._append_value(snapshot, dist)
        result = self._as_tuple()

        return {"times": result[0], "dist": result[1]}
