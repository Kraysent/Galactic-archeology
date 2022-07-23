"""
Task that computes evolution of arbitrary expression over time.
"""
from typing import Callable, Dict

import numpy as np
from amuse.lab import ScalarQuantity, VectorQuantity
from py_expression_eval import Parser

from omtool.core.datamodel import (
    AbstractTask,
    DataType,
    Snapshot,
    get_parameters,
    profiler,
)


class TimeEvolutionTask(AbstractTask):
    """
    Task that computes evolution of arbitrary expression over time.
    """

    functions: Dict[str, Callable[[VectorQuantity], ScalarQuantity]] = {
        "sum": np.sum,
        "mean": np.mean,
        "none": lambda x: x,
    }

    def __init__(
        self,
        expr: str,
        time_unit: ScalarQuantity,
        value_unit: ScalarQuantity,
        function: str = "none",
    ):
        parser = Parser()

        if not expr:
            raise RuntimeError("Expression was empty.")

        self.expr = parser.parse(expr)
        self.function = self.functions[function]
        self.time_unit = time_unit
        self.value_unit = value_unit
        self.times = VectorQuantity([], time_unit.unit)

        if hasattr(value_unit, "unit"):
            self.values = VectorQuantity([], value_unit.unit)
        else:
            self.values = np.array([])

    @profiler("Time evolution task")
    def run(self, snapshot: Snapshot) -> DataType:
        value = self.expr.evaluate(get_parameters(snapshot.particles))
        value = self.function(value)

        self.times.append(snapshot.timestamp)

        if isinstance(self.values, np.ndarray):
            self.values = np.append(self.values, value)
        else:
            self.values.append(value)

        return {"times": self.times / self.time_unit, "values": self.values / self.value_unit}
