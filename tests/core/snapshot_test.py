from omtool.core.utils import BaseTestCase
from omtool.core.datamodel import Snapshot
from amuse.lab import Particles, units, VectorQuantity
import numpy as np


class TestSnapshot(BaseTestCase):
    def test_get_amuse_particles_empty(self):
        particles = Particles()
        particles.position = VectorQuantity([], units.kpc)
        particles.velocity = VectorQuantity([], units.kms)
        particles.mass = VectorQuantity([], units.MSun)
        snapshot = Snapshot(particles)

        actual = snapshot.get_amuse_particles()
        self.assertEqual(len(actual), 0)

    def test_get_amuse_particles_two_particles(self):
        particles = Particles(2)
        particles.position = VectorQuantity(np.array([[1, 1, 1], [2, 2, 2]]), units.kpc)
        particles.velocity = VectorQuantity(np.array([[3, 3, 3], [4, 4, 4]]), units.kms)
        particles.mass = VectorQuantity(np.array([10, 20]), units.MSun)
        snapshot = Snapshot(particles)

        actual = snapshot.get_amuse_particles()
        self.assertAmuseParticlesEqual(actual, particles)
