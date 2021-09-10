from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Union

import numpy as np
from amuse.lab import units
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity
import archeology.analysis.utils as utils
from archeology.datamodel import Snapshot

def get_unit_vectors(names: str) -> np.ndarray:
    output = []

    for name in names:
        result = []
    
        if name == 'x':
            result = [1, 0, 0]
        elif name == 'y':
            result = [0, 1, 0]
        elif name == 'z':
            result = [0, 0, 1]

        output.append(np.array(result))

    return output

class AbstractTask(ABC):
    @abstractmethod
    def run(
        self, snapshot: Snapshot
    ) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        pass

class AbstractPlaneTask(AbstractTask):
    def __init__(self, e1: np.ndarray, e2: np.ndarray):
        self.e1 = self._normalize(e1)
        self.e2 = self._normalize(e2)
    
    def update_basis(self, e1: np.ndarray, e2: np.ndarray):
        self.e1 = self._normalize(e1)
        self.e2 = self._normalize(e2)

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        l = (vector ** 2).sum() ** 0.5

        if l != 0:
            return vector / l
        else: 
            return vector
        
    def get_coordinates(self, vector: VectorQuantity, unit: named_unit = None):
        if units is not None:
            return (
                vector.x.value_in(unit),
                vector.y.value_in(unit),
                vector.z.value_in(unit)
            )
        else:
            return (
                vector[0],
                vector[1],
                vector[2]
            )

    def get_projection(
        self, x: np.ndarray, y: np.ndarray, z: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        e1_coords = x * self.e1[0] + y * self.e1[1] + z * self.e1[2]
        e2_coords = x * self.e2[0] + y * self.e2[1] + z * self.e2[2]

        return (e1_coords, e2_coords)

class Mode(Enum):
    PLAIN = 1
    DENSITY = 2

class AbstractScatterTask(AbstractPlaneTask):
    def __init__(self, e1: np.ndarray, e2: np.ndarray):
        self.mode = Mode.PLAIN

        super().__init__(e1, e2)

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
        (x1, x2) = self.get_projection(*self.get_coordinates(snapshot.particles.position, units.kpc))
        
        return self.apply_mode(x1, x2)

class VelocityScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        (vx1, vx2) = self.get_projection(*self.get_coordinates(snapshot.particles.velocity, units.kms))

        return self.apply_mode(vx1, vx2)

class VelocityProfileTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        r = (particles.position - particles.center_of_mass()).value_in(units.kpc)
        v = (particles.velocity - particles.center_of_mass_velocity()).value_in(units.kms)
        r = (r ** 2).sum(axis = 1) ** 0.5
        v = (v ** 2).sum(axis = 1) ** 0.5

        perm = r.argsort()
        r = r[perm]
        v = v[perm]

        resolution = 1000
        r = r.reshape(-1, resolution).mean(axis = 1)
        v = v.reshape(-1, resolution).mean(axis = 1)

        return (r, v)

class CMTrackTask(AbstractPlaneTask):
    def __init__(self, e1: np.ndarray, e2: np.ndarray):
        self.cmx1, self.cmx2 = np.empty((0,)), np.empty((0,))

        super().__init__(e1, e2)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        (x1, x2) = self.get_projection(*self.get_coordinates(cm, units.kpc))

        self.cmx1 = np.append(self.cmx1, x1)
        self.cmx2 = np.append(self.cmx2, x2)

        return (self.cmx1, self.cmx2)

class NormalVelocityTask(AbstractTask):
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

class KineticEnergyTask(AbstractTask):
    def __init__(self):
        self.times = []
        self.energies = []

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times.append(snapshot.timestamp.value_in(units.Myr))
        self.energies.append(snapshot.particles.kinetic_energy().value_in(units.J))

        return (np.array(self.times), np.array(self.energies))

class PlaneDirectionTask(AbstractPlaneTask):
    def __init__(self, axes: Tuple[int, int], norm: float):
        self.norm = norm

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (e1, e2, e3) = utils.get_galactic_basis(snapshot)
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

class AngularMomentumTask(AbstractPlaneTask):
    def __init__(self, axes: Tuple[int, int], norm: float):
        self.norm = norm

        super().__init__(axes)

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        (e1, e2, e3) = utils.get_galactic_basis(snapshot)
        cm = snapshot.particles.center_of_mass()

        r = 8

        (x1, x2) = self.get_axes(e1)
        (cmx1, cmx2) = self.get_quantity_axes(cm, units.kpc)

        x1 = x1 * r * 3 + cmx1
        x2 = x2 * r * 3 + cmx2

        return (np.array([cmx1, x1]), np.array([cmx2, x2]))

class CMDistanceTask(AbstractTask):
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

class TestLineTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        return (np.array([0, 100]), np.array([0, 100]))


