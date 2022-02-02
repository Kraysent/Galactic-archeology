from typing import Tuple

import numpy as np
from amuse.lab import units
from omtool.analysis.tasks import AbstractTask
from omtool.analysis.utils import math
from omtool.datamodel import Snapshot


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
