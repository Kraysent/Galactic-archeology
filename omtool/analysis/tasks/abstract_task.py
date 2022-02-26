from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from amuse.lab import Particles, units
from omtool.datamodel import Snapshot


class AbstractTask(ABC):
    @abstractmethod
    def run(
        self, snapshot: Snapshot
    ) -> Tuple[np.ndarray, np.ndarray]:
        pass

    def _get_sliced_parameters(self, particles: Particles) -> dict:
        return {
            'x': particles.x,
            'y': particles.y,
            'z': particles.z,
            'vx': particles.vx,
            'vy': particles.vy,
            'vz': particles.vz,
            'm': particles.mass
        }

    def filter_barion_particles(self, snapshot: Snapshot):
        barion_filter = np.array(snapshot.particles.is_barion, dtype = bool)

        return snapshot.particles[barion_filter]

class AbstractTimeTask(AbstractTask):
    def __init__(self):
        self.time_unit = units.Myr
        self.times = []
        self.values = []
    
    def _append_value(self, snapshot, value):
        self.times.append(snapshot.timestamp.value_in(self.time_unit))
        self.values.append(value)

    def _as_tuple(self) -> Tuple[np.ndarray, np.ndarray]:
        return (np.array(self.times), np.array(self.values))
    