from unittest.mock import patch

from amuse.lab import Particles, ScalarQuantity, units

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.models.fits_model import FITSModel


class TestFITSModel(BaseTestCase):
    def _generate_snapshots(self) -> list[tuple[Particles, ScalarQuantity]]:
        particles = [Particles(2), Particles(2)]

        particles[0][0].position = [1, 2, 3] | units.kpc
        particles[0][1].position = [2, 3, 4] | units.kpc
        particles[0][0].velocity = [3, 4, 5] | units.kms
        particles[0][1].velocity = [4, 5, 6] | units.kms
        particles[0].mass = [10, 20] | units.MSun

        particles[1][0].position = [10, 20, 30] | units.kpc
        particles[1][1].position = [20, 30, 40] | units.kpc
        particles[1][0].velocity = [30, 40, 50] | units.kms
        particles[1][1].velocity = [40, 50, 60] | units.kms
        particles[1].mass = [100, 200] | units.MSun

        return [(particles[0], 0 | units.Myr), (particles[1], 1 | units.Myr)]

    @patch("tools.models.fits_model.from_fits")
    def test_run(self, from_fits_mock):
        from_fits_mock.return_value = iter(self._generate_snapshots())
        model = FITSModel("test", 1)
        actual = model.run()
        expected = Snapshot(*self._generate_snapshots()[1])

        self.assertSnapshotsEqual(expected, actual)

    @patch("tools.models.fits_model.from_fits")
    def test_snapshot_index_out_of_range(self, from_fits_mock):
        from_fits_mock.return_value = self._generate_snapshots()
        model = FITSModel("test", 5)
        self.assertRaises(ValueError, model.run)
