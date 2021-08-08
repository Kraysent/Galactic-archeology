from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Union

import numpy as np
from amuse.lab import units
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity
from utils.galactic_utils import get_galactic_basis
from utils.plot_parameters import DrawParameters
from utils.snapshot import Snapshot


class AbstractVisualizerTask(ABC):
    @abstractmethod
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        pass

    @property
    def draw_params(self) -> DrawParameters:
        try:
            return self._draw_params
        except AttributeError:
            return DrawParameters()

    @draw_params.setter
    def draw_params(self, value: DrawParameters):
        self._draw_params = value

class AbstractXYZTask(AbstractVisualizerTask):
    def __init__(self, axes: Tuple[str, str]):
        self.x1_name, self.x2_name = axes

    def get_axes(self, vector) -> Tuple[np.ndarray, np.ndarray]:
        axes = {
            'x': vector[0],
            'y': vector[1],
            'z': vector[2]
        }

        return (axes[self.x1_name], axes[self.x2_name])

    def get_quantity_axes(self, vector, unit: named_unit = None) -> Tuple[np.ndarray, np.ndarray]:
        axes = {
            'x': vector.x,
            'y': vector.y,
            'z': vector.z
        }

        if unit is None:
            return (axes[self.x1_name], axes[self.x2_name])
        else: 
            return (axes[self.x1_name].value_in(unit), axes[self.x2_name].value_in(unit))

class Mode(Enum):
    PLAIN = 1
    DENSITY = 2

class AbstractScatterTask(AbstractXYZTask):
    def __init__(self, 
        axes: Tuple[str, str]
    ):
        self.mode = Mode.PLAIN

        super().__init__(axes = axes)

    def apply_mode(self, 
        x1: np.ndarray, x2: np.ndarray
    ) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        if self.mode == Mode.PLAIN:
            return x1, x2
        elif self.mode == Mode.DENSITY:
            dist, _, _ = np.histogram2d(x1, x2, self.resolution, range = [
                self.edges[:2], self.edges[2:]
            ])
            dist = np.flip(dist.T, axis = 0)

            return dist

    def set_plain_mode(self):
        self.mode = Mode.PLAIN

    def set_density_mode(self, 
        resolution: int, 
        edges: Tuple[float, float, float, float]
    ):
        self.mode = Mode.DENSITY
        self.resolution = resolution
        self.edges = edges

class SpatialScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (x1, x2) = self.get_quantity_axes(snapshot.particles.position, units.kpc)
        
        return self.apply_mode(x1, x2)

class PlaneSpatialScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (e1, e2, e3) = get_galactic_basis(snapshot)
        transition_matrix = np.stack((e1, e2, e3))

        pos = snapshot.particles.position.value_in(units.kpc).T
        new_pos = np.matmul(np.linalg.inv(transition_matrix), pos)

        return self.apply_mode(new_pos[1], new_pos[2])

class VelocityScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (vx1, vx2) = self.get_quantity_axes(snapshot.particles.velocity, units.kms)

        return self.apply_mode(vx1, vx2)

class PlaneVelocityScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])
        transition_matrix = np.stack((e1, e2, e3))

        vel = snapshot.particles.velocity.value_in(units.kms).T
        new_vel = np.matmul(np.linalg.inv(transition_matrix), vel)

        return self.apply_mode(new_vel[1], new_vel[2])

class CMTrackTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[str, str]):
        self.cmx1, self.cmx2 = np.empty((0,)), np.empty((0,))

        super().__init__(axes)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        (x1, x2) = self.get_quantity_axes(cm, units.kpc)

        self.cmx1 = np.append(self.cmx1, x1)
        self.cmx2 = np.append(self.cmx2, x2)

        return (self.cmx1, self.cmx2)

class NormalVelocityTask(AbstractVisualizerTask):
    def __init__(self, 
        pov: VectorQuantity, 
        pov_velocity: VectorQuantity, 
        radius: VectorQuantity,
    ):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_velocity.value_in(units.kms)
        self.radius = radius.value_in(units.kpc)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        r_vec = snapshot.particles.position.value_in(units.kpc) - self.pov
        v_vec = snapshot.particles.velocity.value_in(units.kms) - self.pov_vel
        x, y, z = r_vec[:, 0], r_vec[:, 1], r_vec[:, 2]
        vx, vy, vz = v_vec[:, 0], v_vec[:, 1], v_vec[:, 2]
        
        r = np.sum(r_vec ** 2, axis = 1) ** 0.5

        filter = r < self.radius

        r = r[filter]
        x, y, z = x[filter], y[filter], z[filter]
        vx, vy, vz = vx[filter], vy[filter], vz[filter]

        ex, ey, ez = x / r, y / r, z / r

        v_r = ex * vx + ey * vy + ez * vz

        v_rx, v_ry, v_rz = v_r * ex, v_r * ey, v_r * ez
        v_t = ((vx - v_rx) ** 2 + (vy - v_ry) ** 2 + (vz - v_rz) ** 2) ** 0.5

        return (v_r, v_t)

    def set_pov(self, pov: VectorQuantity, pov_vel: VectorQuantity):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_vel.value_in(units.kms)

class KineticEnergyTask(AbstractVisualizerTask):
    def __init__(self):
        self.times = []
        self.energies = []

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times.append(snapshot.timestamp.value_in(units.Myr))
        self.energies.append(snapshot.particles.kinetic_energy().value_in(units.J))

        return (np.array(self.times), np.array(self.energies))

class PlaneDirectionTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[int, int], norm: float):
        self.norm = norm

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])
        cm = snapshot.particles.center_of_mass()

        r = 8

        (x1, x2) = self.get_axes(e2)
        (x11, x22) = self.get_axes(e3)
        (cmx1, cmx2) = self.get_quantity_axes(cm, units.kpc)

        x1 = x1 * r + cmx1
        x2 = x2 * r + cmx2
        x11 = x11 * r + cmx1
        x22 = x22 * r + cmx2

        return (
            np.array([cmx1, x1, x11, cmx1]), 
            np.array([cmx2, x2, x22, cmx2])
        )

class AngularMomentumTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[int, int], norm: float):
        self.norm = norm

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (e1, e2, e3) = get_galactic_basis(snapshot[0:200000])
        cm = snapshot.particles.center_of_mass()

        r = 8

        (x1, x2) = self.get_axes(e1)
        (cmx1, cmx2) = self.get_quantity_axes(cm, units.kpc)

        x1 = x1 * r * 3 + cmx1
        x2 = x2 * r * 3 + cmx2

        return (np.array([cmx1, x1]), np.array([cmx2, x2]))

class CMDistanceTask(AbstractVisualizerTask):
    def __init__(self, part1: slice, part2: slice):
        self.part1 = part1
        self.part2 = part2
        self.dist = []
        self.time = []

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm1 = snapshot.particles[self.part1].center_of_mass().value_in(units.kpc)
        cm2 = snapshot.particles[self.part2].center_of_mass().value_in(units.kpc)

        dist = ((cm1 - cm2) ** 2).sum() ** 0.5
        self.dist.append(dist)
        self.time.append(snapshot.timestamp.value_in(units.Myr))

        return (np.array(self.time), np.array(self.dist))

class TestLineTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        return (np.array([0, 100]), np.array([0, 100]))


