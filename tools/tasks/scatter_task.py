from amuse.lab import ScalarQuantity
from py_expression_eval import Parser

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, get_parameters, register_task


@register_task(name="ScatterTask")
class ScatterTask(AbstractTask):
    """
    Task that computes a given number of arbitrary expressions.

    Args:
    * `expressions` (`dict[str, str]`): dictionary of the expressions. Each entry is an id of
    expression and the expression itself. Each term in expressions must have compatible units (in
    other words, expression should make physical sense). For example, `x + y` is a valid expression
    and `x + vx` is not.
    * `units` (`dict[str, ScalarQuantity]`): dictionary of units for the output. It must have the
    same keys as `expressions` and have compatible units.

    Returns: dictionary with the same keys as `expressions` input and counted values.

    Examples:
    * This expression will count radius and velocity of every particle.

    >>> ScatterTask(
    >>>    {'r': 'x^2 + y^2 + z^2', 'v': 'vx^2 + vy^2 + vz^2'},
    >>>    {'r': 1 | units.kpc, 'v': 1 | units.kms}
    >>> ).run(snapshot)
    """

    def __init__(
        self,
        expressions: dict[str, str],
        units: dict[str, ScalarQuantity],
    ):
        parser = Parser()

        self.expressions = {id: parser.parse(expr) for id, expr in expressions.items()}
        self.units = units

    @profiler("Scatter task")
    def run(self, snapshot: Snapshot) -> DataType:
        params = get_parameters(snapshot.particles)

        return {id: expr.evaluate(params) / self.units[id] for id, expr in self.expressions.items()}
