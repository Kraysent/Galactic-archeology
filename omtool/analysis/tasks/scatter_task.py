from typing import Tuple

import numpy as np
from amuse.lab import ScalarQuantity
from omtool.analysis.tasks import AbstractTask
from omtool.datamodel import Snapshot, profiler
from physical_evaluator import Parser


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
