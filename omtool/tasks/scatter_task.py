"""
Task that computes arbitrary expression against another arbitrary expression and
plots the points in the corresponding way.
"""
from typing import Tuple

import numpy as np
from amuse.lab import ScalarQuantity
from py_expression_eval import Parser

from omtool.core.datamodel import (
    AbstractTask,
    Snapshot,
    filter_barion_particles,
    get_parameters,
    profiler,
)


class ScatterTask(AbstractTask):
    """
    Task that computes arbitrary expression against another arbitrary expression and
    plots the points in the corresponding way.
    """

    def __init__(
        self,
        x_expr: str,
        y_expr: str,
        x_unit: ScalarQuantity,
        y_unit: ScalarQuantity,
        filter_barion: bool = True,
    ):
        parser = Parser()

        if x_expr == "" or y_expr == "":
            raise RuntimeError("Expression was empty.")

        self.x_expr = parser.parse(x_expr)
        self.y_expr = parser.parse(y_expr)
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.filter_barion = filter_barion

    @profiler("Scatter task")
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles

        # move to actions_before
        if self.filter_barion:
            particles = filter_barion_particles(snapshot)

        params = get_parameters(particles)

        x_value = self.x_expr.evaluate(params)
        y_value = self.y_expr.evaluate(params)

        return (x_value / self.x_unit, y_value / self.y_unit)
