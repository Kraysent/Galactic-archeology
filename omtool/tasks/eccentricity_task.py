from typing import Tuple

import numpy as np
from amuse.lab import units
from numpy import linalg
from omtool.tasks import AbstractTask
from omtool.core.datamodel import Snapshot
from omtool.core.datamodel import profiler


# Not implemented correctly yet
class EccentricityTask(AbstractTask):
    def __init__(self, point_id: int, memory_length: int):
        self.point_id = point_id
        self.memory_length = memory_length
        self.pos = np.zeros((0, 3))
        self.ecc = []
        self.time = []

    def _fit_plane(self, pos) -> Tuple[np.ndarray, np.ndarray]:
        z = pos[:, 2]

        A = pos
        A[:, 2] = [1] * len(z)
        A = np.matrix(A)
        B = np.matrix(pos[:, 2]).T

        # coefficients for function f(x, y) = ax + by + c
        coeffs = np.array((A.T * A).I * A.T * B)

        return coeffs.squeeze()

    @profiler("Eccenticity task")
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        pos = snapshot.particles[self.point_id].position.value_in(units.kpc)
        pos = pos - np.mean(pos, axis=0)
        self.pos = np.append(self.pos, [pos], axis=0)
        self.pos = self.pos[-self.memory_length :]

        if self.pos.shape[0] == 1:
            return ([0], [0])

        coeffs = self._fit_plane(self.pos)

        N = np.array([-coeffs[0], -coeffs[1], 1])
        N = N / linalg.norm(N)
        unit_vector_1 = np.array([1, 0, coeffs[0]])
        unit_vector_1 = unit_vector_1 / linalg.norm(unit_vector_1)
        unit_vector_2 = np.cross(N, unit_vector_1)

        xp = np.dot(self.pos, unit_vector_1)
        yp = np.dot(self.pos, unit_vector_2)

        A = np.vstack([xp**2, xp * yp, yp**2, xp, yp]).T
        b = np.ones_like(xp)
        (A, B, C, D, E) = linalg.lstsq(A, b, rcond=None)[0].squeeze()
        F = 1
        nu = np.sign(
            linalg.det(
                np.array([[A, B / 2, D / 2], [B / 2, C, E / 2], [D / 2, E / 2, F]])
            )
        )
        root = ((A - C) ** 2 + B**2) ** 0.5
        e = ((2 * root) / (nu * (A + C) + root)) ** 0.5

        self.ecc.append(e)
        self.time.append(snapshot.timestamp.value_in(units.Myr))

        return (np.array(self.time), np.array(self.ecc))
