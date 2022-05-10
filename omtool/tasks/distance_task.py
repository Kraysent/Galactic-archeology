"""
Task that computes distance between point and some specified position.
"""

from typing import Tuple, Union

import numpy as np
from amuse.lab import units, VectorQuantity, ScalarQuantity
from omtool.tasks import AbstractTimeTask
from omtool.core.analysis.utils import particle_centers
from omtool.core.datamodel import Snapshot, profiler


class DistanceTask(AbstractTimeTask):
    """
    Task that computes distance between point and some specified position.
    """

    def __init__(
        self,
        start_id: int,
        time_unit: ScalarQuantity = 1 | units.Myr,
        dist_unit: ScalarQuantity = 1 | units.kpc,
        end_coords: VectorQuantity = [0, 0, 0] | units.kpc,
        relative_to: Union[int, str] = "origin",
    ):
        self.start_id = start_id
        self.end_coords = end_coords

        if isinstance(relative_to, int):
            self.relative_to = relative_to
        else:
            self.relative_to = particle_centers.get(relative_to)

        super().__init__(time_unit=time_unit, value_unit=dist_unit)

    @profiler("Distance task")
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        start_pos = snapshot.particles[self.start_id].position

        if isinstance(self.relative_to, int):
            end_pos = snapshot.particles[self.relative_to].position
        else:
            end_pos = self.relative_to(snapshot.particles)
        end_pos += self.end_coords

        dist = (end_pos - start_pos).length()
        self._append_value(snapshot, dist)

        return self._as_tuple()
