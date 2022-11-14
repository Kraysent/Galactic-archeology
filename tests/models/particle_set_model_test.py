from amuse.lab import units

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.models.particle_set_model import ParticleSetModel


class TestParticleSet(BaseTestCase):
    def test_no_particles(self):
        model = ParticleSetModel(
            0, 1 | units.MSun, 5 | units.kms, 1 | units.kpc, 1 | units.kpc, 1 | units.kpc
        )

        actual = model.run()

        self.assertSnapshotsEqual(Snapshot(), actual)

    def test_particle_mass(self):
        model = model = ParticleSetModel(
            10, 100 | units.MSun, 5 | units.kms, 1 | units.kpc, 1 | units.kpc, 1 | units.kpc
        )

        actual = model.run()

        self.assertTrue((actual.particles.mass == 10 | units.MSun).all())

