'''
Task that computes distance between two given points.
'''

from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTimeTask
from omtool.analysis.utils import math
from omtool.datamodel import Snapshot, profiler


class DistanceTask(AbstractTimeTask):
    '''
    Task that computes distance between two given points.
    '''

    def __init__(self, start_id: int, end_id: int):
        self.ids = (start_id, end_id)
        super().__init__()

    @profiler('Distance task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        start, end = self.ids

        r1 = snapshot.particles[start].position.value_in(units.kpc)
        r2 = snapshot.particles[end].position.value_in(units.kpc)

        dist = math.get_lengths(r1 - r2, axis=0)
        self._append_value(snapshot, dist)

        return self._as_tuple()
