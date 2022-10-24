import numpy as np

from omtool.core.tasks import DataType


def fit_polynomial(x: np.ndarray, y: np.ndarray, degree: int) -> tuple[np.ndarray, np.ndarray]:
    coeffs = np.polyfit(x, y, deg=degree)
    fit = np.zeros(shape=x.shape)

    while degree >= 0:
        fit += coeffs[-degree - 1] * x**degree

        degree -= 1

    return x, fit


def fit_2d_action(
    data: DataType, x: str = "x", y: str = "y", fit_type: str = "polynomial", **kwargs
) -> DataType:
    funcs = {"polynomial": fit_polynomial}
    x_arr, y_arr = funcs[fit_type](data[x], data[y], **kwargs)
    data[x] = x_arr
    data[y] = y_arr

    return data
