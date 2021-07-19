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

    @abstractmethod
    def get_draw_params(self) -> DrawParameters:
        pass

class XYTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        return (particles.x.value_in(units.kpc), particles.y.value_in(units.kpc))

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.emph = (200000, -1)

        return params

class ZYTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        return (particles.z.value_in(units.kpc), particles.y.value_in(units.kpc))

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.emph = (200000, -1)

        return params

class EnergyTask(AbstractVisualizerTask):
    def __init__(self) -> None:
        self.times = np.empty((0,))
        self.energies = np.empty((0,))

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times = np.append(self.times, snapshot.timestamp.value_in(units.Myr))
        self.energies = np.append(self.energies, snapshot.particles.kinetic_energy().value_in(units.J))

        return (self.times, self.energies)

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 1
        params.linestyle = 'solid'

        return params

class VxVyTask(AbstractVisualizerTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        return (snapshot.particles.vx.value_in(units.kms), snapshot.particles.vy.value_in(units.kms))

    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 0.02
        params.emph = (200000, -1)

        return params

class NormalVelocityTask(AbstractVisualizerTask):
    def __init__(self, 
        pov: VectorQuantity, pov_velocity: VectorQuantity, 
        radius: VectorQuantity, emph: Tuple[int, int] = (0, 0)
    ):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_velocity.value_in(units.kms)
        self.radius = radius.value_in(units.kpc)
        self.emph = emph
    
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

        for (start, end) in [(0, self.emph[0]), (self.emph[0], self.emph[1]), (self.emph[1], -1)]:
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

        self.new_emph = (len(v_rs[0]), len(v_rs[0]) + len(v_rs[1]))

        return (np.concatenate(v_rs), np.concatenate(v_ts))
        
    def get_draw_params(self) -> DrawParameters:
        params = DrawParameters()
        params.markersize = 0.1
        params.emph = self.new_emph

        return params

    def set_pov(self, pov: VectorQuantity, pov_vel: VectorQuantity):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_vel.value_in(units.kms)

