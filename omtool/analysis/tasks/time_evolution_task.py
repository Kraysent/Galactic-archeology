from typing import Tuple

import numpy as np
from amuse.lab import ScalarQuantity, VectorQuantity
from omtool.analysis.tasks import AbstractTask
from omtool.datamodel import Snapshot, profiler
from py_expression_eval import Parser


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
