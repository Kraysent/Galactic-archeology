from amuse.lab import Particles, units

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.models.particle_model import ParticleModel


class TestParticleModel(BaseTestCase):
    def test_run(self):
        model = ParticleModel(5 | units.MSun)

        actual = model.run()

        particles = Particles(1)
        particles.mass = [5] | units.MSun
        particles.position = [[0, 0, 0]] | units.kpc
        particles.velocity = [[0, 0, 0]] | units.kms
        expected = Snapshot(particles)

        self.assertSnapshotsEqual(actual, expected)
