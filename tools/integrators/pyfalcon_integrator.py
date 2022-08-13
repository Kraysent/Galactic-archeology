import pyfalcon
from amuse.datamodel.particles import Particles
from amuse.lab import units, ScalarQuantity
from omtool.core.datamodel import AbstractIntegrator, Snapshot
from omtool.core.integrators import register_integrator
import numpy as np

attr_unit_dict: dict[str, ScalarQuantity | None] = {
    "position": units.kpc,
    "velocity": units.kms,
    "mass": 232500 * units.MSun,
    "is_barion": None,
}

time_unit = units.Gyr


def _to_vector3(array: np.ndarray):
    return array.reshape(len(array), -1, order="F")


@register_integrator(name="pyfalcon")
class PyfalconIntegrator(AbstractIntegrator):
    """
    Wrapper for pyfalcon module that connects it with OMTool snapshots.
    """

    def __init__(self, eps: ScalarQuantity, kmax: float):
        self.eps = eps.value_in(attr_unit_dict["position"])
        self.delta_time = 0.5**kmax

    def _get_params(self, snapshot: Snapshot) -> tuple[dict[str, np.ndarray], float]:
        params = {}

        for attr, unit in attr_unit_dict.items():
            if hasattr(snapshot.particles, attr):
                if unit is not None:
                    value = getattr(snapshot.particles, attr).value_in(unit)
                else:
                    value = getattr(snapshot.particles, attr)

                params[attr] = value

        time = snapshot.timestamp.value_in(time_unit)

        return params, time

    def leapfrog(self, snapshot: Snapshot) -> Snapshot:
        params, time = self._get_params(snapshot)
        if not hasattr(self, "acc"):
            self.acc, _ = pyfalcon.gravity(params["position"], params["mass"], self.eps)

        params["velocity"] += self.acc * (self.delta_time / 2)
        params["position"] += params["velocity"] * self.delta_time
        self.acc, _ = pyfalcon.gravity(params["position"], params["mass"], self.eps)
        params["velocity"] += self.acc * (self.delta_time / 2)
        time += self.delta_time
        params["position"] = _to_vector3(params["position"])
        params["velocity"] = _to_vector3(params["velocity"])

        new_snapshot = Snapshot(Particles(len(params["mass"])))
        for attr, value in params.items():
            if (u := attr_unit_dict.get(attr, None)) is not None:
                setattr(new_snapshot.particles, attr, value | u)
            else:
                setattr(new_snapshot.particles, attr, value)

        new_snapshot.timestamp = time | time_unit

        return new_snapshot
