import numpy as np
from amuse.lab import ScalarQuantity, VectorQuantity, units
from ellipse import LsqEllipse

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task


def fit_ellipse(x: np.ndarray, y: np.ndarray) -> DataType:
    X = np.array(list(zip(x, y)))
    reg = LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()

    a = max(width, height)
    b = min(width, height)
    e = np.sqrt(1 - b**2 / a**2)

    return {"a": a, "e": e}


@register_task(name="EllipseFitTask")
class EllipseFitTask(AbstractTask):
    """
    Task that computes fitted ellipse parameters given a set of 2D points.

    Dynamic args:
    * `x` (`numpy.ndarray`): array of x coordinates of the points
    * `y` (`numpy.ndarray`): array of y coordinates of the points

    Returns:
    * `a` (`float`): major semiaxis
    * `e` (`float`): eccentiricity
    """

    @profiler("Ellipse fit task")
    def run(self, snapshot: Snapshot, x: np.ndarray, y: np.ndarray) -> DataType:
        return fit_ellipse(x, y)
