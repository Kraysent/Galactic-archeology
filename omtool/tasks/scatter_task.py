"""
Task that computes arbitrary expression against another arbitrary expression and
plots the points in the corresponding way.
"""
from typing import List, Tuple

import numpy as np
from amuse.lab import ScalarQuantity, units
from py_expression_eval import Parser

from omtool.core.datamodel import (
    AbstractTask,
    Snapshot,
    filter_barion_particles,
    get_parameters,
    profiler,
)
from omtool.core.datamodel import DataType


class ScatterTask(AbstractTask):
    """
    Task that computes arbitrary expression against another arbitrary expression and
    plots the points in the corresponding way.
    """

    def __init__(
        self,
        expressions: dict[str, str],
        units: dict[str, ScalarQuantity],
        filter_barion: bool = True,
    ):
        parser = Parser()

        self.expressions = {id: parser.parse(expr) for id, expr in expressions.items()}
        self.units = units
        self.filter_barion = filter_barion

    @profiler("Scatter task")
    def run(self, snapshot: Snapshot) -> DataType:
        particles = snapshot.particles

        # move to actions_before
        if self.filter_barion:
            particles = filter_barion_particles(snapshot)

        params = get_parameters(particles)

        res = {}
        for id, expr in self.expressions.items():
            res[id] = expr.evaluate(params) / self.units[id]

        return res
