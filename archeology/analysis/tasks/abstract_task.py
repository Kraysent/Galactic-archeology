from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Tuple, Union

import numpy as np
from amuse.lab import units
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity
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
 
def filter_barion_particles(snapshot: Snapshot):
    barion_filter = np.array(snapshot.particles.is_barion, dtype = bool)

    return snapshot.particles[barion_filter]

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
        particles = filter_barion_particles(snapshot)
        (x1, x2) = self.get_projection(*self.get_coordinates(particles.position, units.kpc))
        
        return self.apply_mode(x1, x2)

class VelocityScatterTask(AbstractScatterTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        particles = filter_barion_particles(snapshot)
        (vx1, vx2) = self.get_projection(*self.get_coordinates(particles.velocity, units.kms))

        return self.apply_mode(vx1, vx2)

class VelocityProfileTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        cm_vel = snapshot.particles.center_of_mass_velocity()

        particles = filter_barion_particles(snapshot)

        r = (particles.position - cm).value_in(units.kpc)
        v = (particles.velocity - cm_vel).value_in(units.kms)
        r = (r ** 2).sum(axis = 1) ** 0.5
        v = (v ** 2).sum(axis = 1) ** 0.5

        perm = r.argsort()
        r = r[perm]
        v = v[perm]

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution
        r = r[0:number_of_chunks].reshape(-1, resolution).mean(axis = 1)
        v = v[0:number_of_chunks].reshape(-1, resolution).mean(axis = 1)

        return (r, v)

class MassProfileTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        cm = particles.center_of_mass()

        r = (particles.position - cm).value_in(units.kpc)
        m = particles.mass.value_in(units.MSun)
        r = (r ** 2).sum(axis = 1) ** 0.5

        perm = r.argsort()
        r = r[perm]
        m = m[perm]

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution

        r = r[0:number_of_chunks:resolution]
        m = m[0:number_of_chunks].reshape(-1, resolution).sum(axis = 1)
        m = np.cumsum(m)

        return (r, m)

class PointEmphasisTask(AbstractPlaneTask):
    def __init__(self, point_id: int, e1: np.ndarray, e2: np.ndarray):
        self.point_id = point_id

        super().__init__(e1, e2)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        vector = snapshot.particles[self.point_id].position
        (x1, x2) = self.get_projection(*self.get_coordinates(vector, units.kpc))

        return (x1, x2)

class NormalVelocityTask(AbstractTask):
    def __init__(self,
        pov_updater: Callable[[Snapshot], Tuple[VectorQuantity, VectorQuantity]],
        radius: VectorQuantity
    ):
        self.pov_updater = pov_updater
        self.radius = radius.value_in(units.kpc)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        pov, pov_vel = self.pov_updater(snapshot)

        particles = filter_barion_particles(snapshot)

        r_vec = (particles.position - pov).value_in(units.kpc)
        v_vec = (particles.velocity - pov_vel).value_in(units.kms)
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

class KineticEnergyTask(AbstractTask):
    def __init__(self):
        self.times = []
        self.energies = []

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self.times.append(snapshot.timestamp.value_in(units.Myr))
        self.energies.append(snapshot.particles.kinetic_energy().value_in(units.J))

        return (np.array(self.times), np.array(self.energies))

class DistanceTask(AbstractTask):
    def __init__(self, start_id: int, end_id: int):
        self.ids = (start_id, end_id)
        self.dist = []
        self.time = []

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        start, end = self.ids

        v1 = snapshot.particles[start].position.value_in(units.kpc)
        v2 = snapshot.particles[end].position.value_in(units.kpc)

        dist = ((v1 - v2) ** 2).sum() ** 0.5
        self.dist.append(dist)
        self.time.append(snapshot.timestamp.value_in(units.Myr))

        return (np.array(self.time), np.array(self.dist))
