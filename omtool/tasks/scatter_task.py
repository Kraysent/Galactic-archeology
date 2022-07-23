from amuse.lab import ScalarQuantity
from py_expression_eval import Parser

from omtool.core.datamodel import (
    AbstractTask,
    DataType,
    Snapshot,
    filter_barion_particles,
    get_parameters,
    profiler,
)


class ScatterTask(AbstractTask):
    """Task that computes a given number of arbitrary expressions

    :param expressions: dictionary that describes expressions and their names
    :type expressions: dict[str, str]

    :param units: dictionary that describes units corresponding to each expression and their names
    :type units: dict[str, ScalarQuantity]
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

        # TODO: move to actions_before
        if self.filter_barion:
            particles = filter_barion_particles(snapshot)

        params = get_parameters(particles)

        return {id: expr.evaluate(params) / self.units[id] for id, expr in self.expressions.items()}
