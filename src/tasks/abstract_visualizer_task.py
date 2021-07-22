from abc import ABC, abstractmethod
from typing import Tuple, Union
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity

import numpy as np
from amuse.lab import units

from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot


class AbstractVisualizerTask(ABC):    
    @abstractmethod
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        pass

    @property
    def plot_params(self) -> PlotParameters:
        try:
            return self._plot_params
        except AttributeError:
            return PlotParameters()

    @plot_params.setter
    def plot_params(self, value: PlotParameters):
        self._plot_params = value

    @property
    def draw_params(self) -> DrawParameters:
        try:
            return self._draw_params
        except AttributeError:
            return DrawParameters()

    @draw_params.setter
    def draw_params(self, value: DrawParameters):
        self._draw_params = value

    @property
    def blocks(self) -> Tuple[Tuple[int, int], ...]:
        if hasattr(self, '_blocks'):
            return getattr(self, '_blocks')
        else:
            return ((0, None), )

    @blocks.setter
    def blocks(self, value: Tuple[Tuple[int, int], ...]):
        self._blocks = value

class AbstractXYZTask(AbstractVisualizerTask):
    def __init__(self, axes: Tuple[str, str]):
        self.x1, self.x2 = axes

    def get_axes(self, vector, unit: named_unit = None) -> Tuple[np.ndarray, np.ndarray]:
        axes = {
            'x': vector.x,
            'y': vector.y,
            'z': vector.z
        }

        if unit is None:
            return (axes[self.x1], axes[self.x2])
        else: 
            return (axes[self.x1].value_in(unit), axes[self.x2].value_in(unit))

class PlaneScatterTask(AbstractXYZTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (x1, x2) = self.get_axes(snapshot.particles.position)

        return x1, x2

class SlicedCMTrackTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[str, str], slice: Tuple[int, int]):
        self.cmx1, self.cmx2 = np.empty((0,)), np.empty((0,))
        self.slice = slice

        super().__init__(axes)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles[self.slice[0]: self.slice[1]].center_of_mass()
        (x1, x2) = self.get_axes(cm, units.kpc)

        self.cmx1 = np.append(self.cmx1, x1)
        self.cmx2 = np.append(self.cmx2, x2)

        return (self.cmx1, self.cmx2)

class PlaneDensityTask(AbstractXYZTask):
    def __init__(self,
        axes: Tuple[str, str],
        edges: Tuple[float, float, float, float], 
        resolution: int
    ):
        self.edges = edges
        self.resolution = resolution

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> np.ndarray:
        (x1, x2) = self.get_axes(snapshot.particles.position, units.kpc)
        
        dist, _, _ = np.histogram2d(x1, x2, self.resolution, range = [
            self.edges[:2], self.edges[2:]
        ])

        return np.flip(dist.T, axis = 0)

class VProjectionTask(AbstractXYZTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (vx1, vx2) = self.get_axes(snapshot.particles.velocity, units.kms)

        return (vx1, vx2)

class NormalVelocityTask(AbstractVisualizerTask):
    def __init__(self, 
        pov: VectorQuantity, pov_velocity: VectorQuantity, radius: VectorQuantity
    ):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_velocity.value_in(units.kms)
        self.radius = radius.value_in(units.kpc)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        r_vec = snapshot.particles.position.value_in(units.kpc) - self.pov
        v_vec = snapshot.particles.velocity.value_in(units.kms) - self.pov_vel
        x, y, z = r_vec[0], r_vec[1], r_vec[2]
        vx, vy, vz = v_vec[0], v_vec[1], v_vec[2]
        
        r = np.sum(r_vec ** 2, axis = 0) ** 0.5
        v_rs = []
        v_ts = []

        for (start, end) in self._blocks:
            curr_r = r[start:end]
            filter = curr_r < self.radius

            curr_x, curr_y, curr_z = x[start:end][filter], y[start:end][filter], z[start:end][filter]
            curr_vx, curr_vy, curr_vz = vx[start:end][filter], vy[start:end][filter], vz[start:end][filter]
            curr_r = curr_r[filter]

            ex, ey, ez = curr_x / curr_r, curr_y / curr_r, curr_z / curr_r

            v_r = ex * curr_vx + ey * curr_vy + ez * curr_vz

            v_rx, v_ry, v_rz = v_r * ex, v_r * ey, v_r * ez
            v_t = ((curr_vx - v_rx) ** 2 + (curr_vy - v_ry) ** 2 + (curr_vz - v_rz) ** 2) ** 0.5

            v_rs.append(v_r)
            v_ts.append(v_t)

        self._new_blocks = []
        ind = len(v_rs[0])
        self._new_blocks.append((0, ind))

        for i in range(len(v_rs) - 2):
            self._new_blocks.append((ind, ind + len(v_rs[i + 1])))
            ind = ind + len(v_rs[i + 1])
    
        self._new_blocks.append((ind, -1))
        self._new_blocks = tuple(self._new_blocks)

        return (np.concatenate(v_rs), np.concatenate(v_ts))
        
    @AbstractVisualizerTask.blocks.getter
    def blocks(self) -> Tuple[Tuple[int, int], ...]:
        try:
            return self._new_blocks
        except AttributeError:
            return self._blocks

    def set_pov(self, pov: VectorQuantity, pov_vel: VectorQuantity):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_vel.value_in(units.kms)

class KineticEnergyTask(AbstractVisualizerTask):
    def __init__(self):
        self.times = np.empty((0,))
        self.energies = np.empty((0,))

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times = np.append(self.times, snapshot.timestamp.value_in(units.Myr))
        self.energies = np.append(
            self.energies,
            snapshot.particles.kinetic_energy().value_in(units.J)
        )

        return (self.times, self.energies)

class SliceAngularMomentumTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[int, int], slice: Tuple[int, int], norm: float):
        self.slice = slice
        self.norm = norm

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        snapshot = snapshot[self.slice[0]: self.slice[1]]
        cm = snapshot.particles.center_of_mass()
        ang_momentum = snapshot.particles.total_angular_momentum()
        length = ang_momentum.length().value_in(units.m ** 2 * units.kg * units.s ** -1)
        (x1, x2) = self.get_axes(
            ang_momentum, units.m ** 2 * units.kg * units.s ** -1
        )
        (cmx1, cmx2) = self.get_axes(
            cm, units.kpc
        )
        x1 = x1 / length * self.norm + cmx1
        x2 = x2 / length * self.norm + cmx2

        return (np.array([cmx1, x1]), np.array([cmx2, x2]))

class TestLineTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        return (np.array([0, 100]), np.array([0, 100]))


