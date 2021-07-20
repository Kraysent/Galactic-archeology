from abc import ABC, abstractmethod
from typing import Tuple
from amuse.units.quantities import VectorQuantity

import numpy as np
from amuse.lab import units

from utils.plot_parameters import DrawParameters, PlotParameters
from utils.snapshot import Snapshot


class AbstractVisualizerTask(ABC):    
    @abstractmethod
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        pass

    @property
    def plot_params(self) -> PlotParameters:
        if self._plot_params is not None:
            return self._plot_params
        else:
            raise RuntimeError('No plot parameters specified for the task.')

    @plot_params.setter
    def plot_params(self, value: PlotParameters):
        self._plot_params = value

    @property
    def blocks(self) -> Tuple[Tuple[int, int], ...]:
        if hasattr(self, '_blocks'):
            return getattr(self, '_blocks')
        else:
            return ((0, -1), )

    @blocks.setter
    def blocks(self, value: Tuple[Tuple[int, int], ...]):
        self._blocks = value

    @abstractmethod
    def get_draw_params(self) -> DrawParameters:
        pass

class XYTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        return (particles.x.value_in(units.kpc), particles.y.value_in(units.kpc))

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.blocks_color = ('b', 'r')

        return params

class XYSliceCMTrackTask(AbstractVisualizerTask):
    def __init__(self, slice: Tuple[int, int]) -> None:
        self.cmx = np.empty((0,))
        self.cmy = np.empty((0,))
        self.slice = slice

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles[self.slice[0]: self.slice[1]].center_of_mass()
        self.cmx = np.append(self.cmx, cm.x.value_in(units.kpc))
        self.cmy = np.append(self.cmy, cm.y.value_in(units.kpc))

        return (self.cmx, self.cmy)

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.linestyle = 'solid'
        params.blocks_color = 'g'
        params.marker = 'None'

        return params

class ZYTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        return (particles.z.value_in(units.kpc), particles.y.value_in(units.kpc))

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.blocks_color = ('b', 'r')

        return params

class EnergyTask(AbstractVisualizerTask):
    def __init__(self) -> None:
        self.times = np.empty((0,))
        self.energies = np.empty((0,))

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times = np.append(self.times, snapshot.timestamp.value_in(units.Myr))
        self.energies = np.append(
            self.energies,
            snapshot.particles.kinetic_energy().value_in(units.J)
        )

        return (self.times, self.energies)

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 1
        params.linestyle = 'solid'

        return params

class VxVyTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        return (
            snapshot.particles.vx.value_in(units.kms), 
            snapshot.particles.vy.value_in(units.kms)
        )

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 0.02
        params.blocks_color = ('b', 'r')

        return params

class NormalVelocityTask(AbstractVisualizerTask):
    def __init__(self, 
        pov: VectorQuantity, pov_velocity: VectorQuantity, radius: VectorQuantity
    ):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_velocity.value_in(units.kms)
        self.radius = radius.value_in(units.kpc)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        x = snapshot.particles.x.value_in(units.kpc) - self.pov[0]
        y = snapshot.particles.y.value_in(units.kpc) - self.pov[1]
        z = snapshot.particles.z.value_in(units.kpc) - self.pov[2]
        vx = snapshot.particles.vx.value_in(units.kms) - self.pov_vel[0]
        vy = snapshot.particles.vy.value_in(units.kms) - self.pov_vel[1]
        vz = snapshot.particles.vz.value_in(units.kms) - self.pov_vel[2]
        
        r = (x ** 2 + y ** 2 + z ** 2) ** 0.5
        v_rs = []
        v_ts = []

        for (start, end) in self.blocks:
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

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 0.1
        params.blocks_color = ('b', 'r')

        return params

    def set_pov(self, pov: VectorQuantity, pov_vel: VectorQuantity):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_vel.value_in(units.kms)

