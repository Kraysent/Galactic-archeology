from typing import Tuple

import numpy as np

DataType = Tuple[np.ndarray, np.ndarray]


def fit_polynomial(data: DataType, degree: int) -> DataType:
    coeffs = np.polyfit(data[0], data[1], deg=degree)
    fit = np.zeros(shape=data[0].shape)

    while degree >= 0:
        fit += coeffs[-degree - 1] * data[0] ** degree

        degree -= 1

    return (data[0], fit)


def fit_action(data: DataType, fit_type: str = "polynomial", **kwargs) -> DataType:
    funcs = {"polynomial": fit_polynomial}

    return funcs.get(fit_type, fit_polynomial)(data, **kwargs)
