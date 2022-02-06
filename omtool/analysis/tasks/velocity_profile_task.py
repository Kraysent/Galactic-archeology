from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTask
from omtool.analysis.utils import math
from omtool.datamodel import Snapshot
from omtool.datamodel.task_profiler import profiler


class VelocityProfileTask(AbstractTask):
    @profiler
    def run(self, snapshot: Snapshot) -> Tuple[np.ndarray, np.ndarray]:
        cm = snapshot.particles.center_of_mass()
        cm_vel = snapshot.particles.center_of_mass_velocity()

        particles = self.filter_barion_particles(snapshot)

        r = math.get_lengths(particles.position - cm)
        v = math.get_lengths(particles.velocity - cm_vel)
        (r, v) = math.sort_with(r, v)

        resolution = 1000
        number_of_chunks = (len(r) // resolution) * resolution
        r = r[0:number_of_chunks:resolution]
        v = v[0:number_of_chunks].reshape((-1, resolution)).mean(axis = 1)

        return (r.value_in(units.kpc), v.value_in(units.kms))
