from abc import ABC, abstractmethod
from typing import Tuple, Union
from enum import Enum

import numpy as np
from amuse.datamodel.particles import Particles
from amuse.lab import units
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity
from utils.plot_parameters import DrawParameters
from utils.snapshot import Snapshot


class AbstractVisualizerTask(ABC):
    def __init__(self, part: slice = slice(0, None, None)):
        self.part = part

    def execute(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        return self.run(snapshot[self.part])

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
    def __init__(self, axes: Tuple[str, str], part: slice = slice(0, None, None)):
        self.x1_name, self.x2_name = axes

        super().__init__(part)

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
        axes: Tuple[str, str], 
        part: slice = slice(0, None, None)
    ):
        self.mode = Mode.PLAIN

        super().__init__(axes = axes, part = part)

    def get_data(self, 
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
        
        return self.get_data(x1, x2)

class VelocityScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (vx1, vx2) = self.get_quantity_axes(snapshot.particles.velocity, units.kms)

        return self.get_data(vx1, vx2)

class CMTrackTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[str, str], part: slice = slice(0, None, None)):
        self.cmx1, self.cmx2 = np.empty((0,)), np.empty((0,))

        super().__init__(axes, slice)
    
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
        part: slice = slice(0, None, None)
    ):
        self.pov = pov.value_in(units.kpc)
        self.pov_vel = pov_velocity.value_in(units.kms)
        self.radius = radius.value_in(units.kpc)

        super().__init__(part)
    
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
    def __init__(self, part: slice = slice(0, None, None)):
        self.times = np.empty((0,))
        self.energies = np.empty((0,))

        super().__init__(part)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times = np.append(self.times, snapshot.timestamp.value_in(units.Myr))
        self.energies = np.append(
            self.energies,
            snapshot.particles.kinetic_energy().value_in(units.J)
        )

        return (self.times, self.energies)

class PlaneDirectionTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[int, int], norm: float, part: slice = slice(0, None, None)):
        self.norm = norm

        super().__init__(axes, part)

    def _get_angular_momentum(self, particles: Particles) -> np.ndarray:
        r = particles.position.value_in(units.kpc)
        v = particles.velocity.value_in(units.kms)
        cm = particles.center_of_mass().value_in(units.kpc)
        cm_vel = particles.center_of_mass_velocity().value_in(units.kms)
        m = particles.mass.value_in(units.MSun)

        r = r - cm
        v = v - cm_vel
        ang_momentum = m[:, np.newaxis] * np.cross(v, r)
        total_ang_momentum = np.sum(ang_momentum, axis = 0)
        return total_ang_momentum

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        ang_momentum = self._get_angular_momentum(snapshot.particles)

        r = 8

        plane_vector = np.empty(ang_momentum.shape)
        plane_vector[0] = 1
        plane_vector[1] = 1
        plane_vector[2] = - plane_vector[0] * ang_momentum[0] / ang_momentum[2] - plane_vector[1] * ang_momentum[1] / ang_momentum[2] 

        length = (plane_vector ** 2).sum() ** 0.5

        (x1, x2) = self.get_axes(plane_vector)
        (cmx1, cmx2) = self.get_quantity_axes(cm, units.kpc)

        x1 = x1 / length * self.norm + cmx1
        x2 = x2 / length * self.norm + cmx2

        return (np.array([cmx1, x1]), np.array([cmx2, x2]))

class AngularMomentumTask(AbstractXYZTask):
    def __init__(self, axes: Tuple[int, int], norm: float, part: slice = slice(0, None, None)):
        self.norm = norm

        super().__init__(axes, part)

    def _get_angular_momentum(self, particles: Particles) -> np.ndarray:
        r = particles.position.value_in(units.kpc)
        v = particles.velocity.value_in(units.kms)
        cm = particles.center_of_mass().value_in(units.kpc)
        cm_vel = particles.center_of_mass_velocity().value_in(units.kms)
        m = particles.mass.value_in(units.MSun)

        r = r - cm
        v = v - cm_vel
        ang_momentum = m[:, np.newaxis] * np.cross(v, r)
        total_ang_momentum = np.sum(ang_momentum, axis = 0)
        return total_ang_momentum

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        ang_momentum = self._get_angular_momentum(snapshot.particles)
        length = (ang_momentum ** 2).sum() ** 0.5

        r = 8

        (x1, x2) = self.get_axes(ang_momentum)
        (cmx1, cmx2) = self.get_quantity_axes(cm, units.kpc)

        x1 = x1 / length * self.norm + cmx1
        x2 = x2 / length * self.norm + cmx2

        return (np.array([cmx1, x1]), np.array([cmx2, x2]))

class CMDistanceTask(AbstractVisualizerTask):
    def __init__(self, part1: slice, part2: slice):
        self.part1 = part1
        self.part2 = part2
        self.dist = []
        self.time = []

        super().__init__()

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


