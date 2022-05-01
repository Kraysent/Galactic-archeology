from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.core.analysis.tasks import AbstractTask
from omtool.core.analysis.tasks.abstract_task import filter_barion_particles
from omtool.core.analysis.utils import math, particle_centers
from omtool.core.datamodel import Snapshot, profiler


class VelocityProfileTask(AbstractTask):
    '''
    Task that computes radial velocity distribution. 
    '''

    def __init__(self, center_type: str = 'mass', resolution: int = 1000) -> None:
        super().__init__()
        self.center_func = particle_centers.get(center_type)
        self.center_vel_func = particle_centers.get_velocity(center_type)
        self.resolution = resolution

    @profiler('Velocity profile task')
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        center = self.center_func(snapshot.particles)
        center_vel = self.center_vel_func(snapshot.particles)

        particles = filter_barion_particles(snapshot)

        r = math.get_lengths(particles.position - center)
        v = math.get_lengths(particles.velocity - center_vel)
        (r, v) = math.sort_with(r, v)

        number_of_chunks = (len(r) // self.resolution) * self.resolution
        r = r[0:number_of_chunks:self.resolution]
        v = v[0:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        return (r.value_in(units.kpc), v.value_in(units.kms))
