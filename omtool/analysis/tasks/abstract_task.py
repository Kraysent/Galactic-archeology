from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from amuse.lab import units, Particles
from amuse.units.quantities import VectorQuantity, ScalarQuantity
from omtool.datamodel import Snapshot
from physical_evaluator import Parser

from omtool.datamodel.task_profiler import profiler

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
    
class ScatterTask(AbstractTask):
    def __init__(self, x_expr: str, y_expr: str, x_unit: ScalarQuantity, y_unit: ScalarQuantity):
        parser = Parser()

        self.x_unit = x_unit
        self.y_unit = y_unit
        self.x_expr = parser.parse(x_expr)
        self.y_expr = parser.parse(y_expr)

    @profiler('Scatter task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = self.filter_barion_particles(snapshot)
        params = self._get_sliced_parameters(particles)
        
        x_value = self.x_expr.evaluate(params)
        y_value = self.y_expr.evaluate(params)

        return (x_value / self.x_unit, y_value / self.y_unit)

class TimeEvolutionTask(AbstractTask):
    functions = {
        'sum': np.sum,
        'mean': np.mean,
        'none': lambda x: x
    }

    def __init__(self, expr: str, time_unit: ScalarQuantity, value_unit: ScalarQuantity,  function: str = 'none'):
        parser = Parser()

        self.expr = parser.parse(expr)
        self.function = self.functions[function]
        self.time_unit = time_unit
        self.value_unit = value_unit
        self.times = VectorQuantity([], time_unit.unit)
        self.values = VectorQuantity([], value_unit.unit)

    @profiler('Time evolution task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        value = self.expr.evaluate(self._get_sliced_parameters(snapshot.particles))
        value = self.function(value)

        self.times.append(snapshot.timestamp)
        self.values.append(value)

        return (self.times / self.time_unit, self.values / self.value_unit)
