'''
Abstract tasks' classes. Import this if you want to create your own task.
'''
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from amuse.lab import Particles, units
from omtool.core.datamodel import Snapshot


def get_sliced_parameters(particles: Particles) -> dict:
    '''
    Returns parameters of the particle set that can be used in expression evaluation.
    '''
    return {
        'x': particles.x,
        'y': particles.y,
        'z': particles.z,
        'vx': particles.vx,
        'vy': particles.vy,
        'vz': particles.vz,
        'm': particles.mass
    }


def filter_barion_particles(snapshot: Snapshot):
    '''
    Filters out non-barion particles from the snapshot.
    '''
    barion_filter = np.array(snapshot.particles.is_barion, dtype=bool)

    return snapshot.particles[barion_filter]


class AbstractTask(ABC):
    '''
    Base class for the tasks that operate on snapshots.
    '''
    @abstractmethod
    def run(
        self, snapshot: Snapshot
    ) -> Tuple[np.ndarray, np.ndarray]:
        '''
        Runs the task on given snapshot.
        '''


class AbstractTimeTask(AbstractTask):
    '''
    Base class for all tasks that show evolution of some value over time.
    '''

    def __init__(self):
        self.time_unit = units.Myr
        self.times = []
        self.values = []

    def _append_value(self, snapshot, value):
        self.times.append(snapshot.timestamp.value_in(self.time_unit))
        self.values.append(value)

    def _as_tuple(self) -> Tuple[np.ndarray, np.ndarray]:
        return (np.array(self.times), np.array(self.values))
