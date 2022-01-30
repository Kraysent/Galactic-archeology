from abc import ABC, abstractmethod
from typing import Tuple, Union

import numpy as np
import numpy.linalg as linalg
from amuse.lab import units, constants
from amuse.units.core import named_unit
from amuse.units.quantities import VectorQuantity
from omtool.analysis.utils.pyfalcon_analizer import get_potentials
from omtool.datamodel import Snapshot
import omtool.analysis.utils as math

class AbstractTask(ABC):
    @abstractmethod
    def run(
        self, snapshot: Snapshot
    ) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        pass

def get_task(task_name: str, args: dict) -> AbstractTask:
    task_map = {
        'SpatialScatterTask': SpatialScatterTask,
        'VelocityScatterTask': VelocityScatterTask,
        'DistanceTask': DistanceTask,
        'VelocityProfileTask': VelocityProfileTask,
        'MassProfileTask': MassProfileTask,
        'PointEmphasisTask': PointEmphasisTask,
        'EccentricityTask': EccentricityTask,
        'PotentialTask': PotentialTask,
        'BoundMassTask': BoundMassTask
    }

    return task_map[task_name](**args)

def filter_barion_particles(snapshot: Snapshot):
    barion_filter = np.array(snapshot.particles.is_barion, dtype = bool)

    return snapshot.particles[barion_filter]

class AbstractTimeTask(AbstractTask):
    def __init__(self):
        self.time_unit = units.Myr
        self.times = []
        self.values = []
    
    def _append_value(self, snapshot, value):
        self.times.append(snapshot.timestamp.value_in(self.time_unit))
        self.values.append(value)

    def _as_tuple(self) -> Tuple[np.ndarray, np.ndarray]:
        return (np.array(self.times), np.array(self.values))
        
class AbstractPlaneTask(AbstractTask):
    def __init__(self, e1: VectorQuantity, e2: VectorQuantity):
        self.e1 = e1
        self.e2 = e2
        
    def get_projection(
        self, r: VectorQuantity
    ) -> Tuple[np.ndarray, np.ndarray]:
        e1_coords = r.x * self.e1.x + r.y * self.e1.y + r.z * self.e1.z
        e2_coords = r.x * self.e2.x + r.y * self.e2.y + r.z * self.e2.z

        return (e1_coords / self.e1.length() ** 2, e2_coords / self.e2.length() ** 2)

class SpatialScatterTask(AbstractPlaneTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        particles = filter_barion_particles(snapshot)
        (x1, x2) = self.get_projection(particles.position)
        
        return x1, x2

class VelocityScatterTask(AbstractPlaneTask):
    def run(self, snapshot: Snapshot) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        particles = filter_barion_particles(snapshot)
        (vx1, vx2) = self.get_projection(particles.velocity)

        return vx1, vx2

class PotentialTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        particles = snapshot.particles

        r = math.get_lengths(particles.position - cm)
        potentials = get_potentials(snapshot.particles, 0.2 | units.kpc)
        (r, potentials) = math.sort_with(r, potentials)

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution

        r = r[0:number_of_chunks:resolution]
        potentials = potentials[0:number_of_chunks].reshape((-1, resolution)).mean(axis = 1)
        potentials = potentials / potentials.mean()

        return (r.value_in(units.kpc), potentials)

class BoundMassTask(AbstractTimeTask):
    def __init__(self):
        super().__init__()

    def _get_bound_particles(self, particles):
        potentials = get_potentials(particles, 0.2 | units.kpc)
        velocities = math.get_lengths(particles.velocity - particles.center_of_mass_velocity())
        full_specific_energies = potentials + velocities ** 2 / 2

        return particles[full_specific_energies < (0 | units.J / units.MSun)]

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        bound_particles = self._get_bound_particles(snapshot.particles)
        bound_particles = self._get_bound_particles(bound_particles)
        bound_particles = self._get_bound_particles(bound_particles)

        self._append_value(snapshot, bound_particles.total_mass().value_in(units.MSun))

        return self._as_tuple()

class VelocityProfileTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        cm_vel = snapshot.particles.center_of_mass_velocity()

        particles = filter_barion_particles(snapshot)

        r = math.get_lengths(particles.position - cm)
        v = math.get_lengths(particles.velocity - cm_vel)
        (r, v) = math.sort_with(r, v)

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution
        r = r[0:number_of_chunks:resolution]
        v = v[0:number_of_chunks].reshape((-1, resolution)).mean(axis = 1)

        return (r.value_in(units.kpc), v.value_in(units.kms))

class MassProfileTask(AbstractTask):
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        particles = snapshot.particles
        cm = particles.center_of_mass()

        r = math.get_lengths(particles.position - cm)
        m = particles.mass
        (r, m) = math.sort_with(r, m)

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution

        r = r[0:number_of_chunks:resolution]
        m = m[0:number_of_chunks].reshape((-1, resolution)).sum(axis = 1)
        m = np.cumsum(m)

        return (r.value_in(units.kpc), m.value_in(units.MSun))

class PointEmphasisTask(AbstractPlaneTask):
    def __init__(self, point_id: int, e1: VectorQuantity, e2: VectorQuantity):
        self.point_id = point_id

        super().__init__(e1, e2)
    
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        vector = snapshot.particles[self.point_id].position
        (x1, x2) = self.get_projection(vector)

        return (x1, x2)

class KineticEnergyTask(AbstractTimeTask):
    def __init__(self):
        super().__init__()

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        self._append_value(snapshot, snapshot.particles.kinetic_energy().value_in(units.J))

        return self._as_tuple()

class DistanceTask(AbstractTimeTask):
    def __init__(self, start_id: int, end_id: int):
        self.ids = (start_id, end_id)
        super().__init__()

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        start, end = self.ids

        r1 = snapshot.particles[start].position.value_in(units.kpc)
        r2 = snapshot.particles[end].position.value_in(units.kpc)

        dist = math.get_lengths(r1 - r2, axis = 0)
        self._append_value(snapshot, dist)

        return self._as_tuple()

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
        B = np.matrix(pos[:, 2] ).T
        
        # coefficients for function f(x, y) = ax + by + c
        coeffs = np.array((A.T * A).I * A.T * B)

        return coeffs.squeeze()

    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        pos = snapshot.particles[self.point_id].position.value_in(units.kpc)
        pos = pos - np.mean(pos, axis = 0)
        self.pos = np.append(self.pos, [pos], axis = 0)
        self.pos = self.pos[-self.memory_length:]
        
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

        A = np.vstack([xp ** 2, xp * yp, yp ** 2, xp, yp]).T
        b = np.ones_like(xp)
        (A, B, C, D, E) = linalg.lstsq(A, b, rcond = None)[0].squeeze()
        F = 1
        nu = np.sign(linalg.det(np.array([
            [A, B / 2, D / 2],
            [B / 2, C, E / 2],
            [D / 2, E / 2, F]
        ])))
        root = ((A - C) ** 2 + B ** 2) ** 0.5
        e = ((2 * root) / (nu * (A + C) + root)) ** 0.5

        self.ecc.append(e)
        self.time.append(snapshot.timestamp.value_in(units.Myr))

        return (np.array(self.time), np.array(self.ecc))