from unittest.mock import patch

from amuse.lab import Particles, units

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.models.fits_model import FITSModel


class TestFITSModel(BaseTestCase):
    def _generate_snapshots(self) -> list[Snapshot]:
        particles_list = [Particles(2), Particles(2)]

        particles_list[0][0].position = [1, 2, 3] | units.kpc
        particles_list[0][1].position = [2, 3, 4] | units.kpc
        particles_list[0][0].velocity = [3, 4, 5] | units.kms
        particles_list[0][1].velocity = [4, 5, 6] | units.kms
        particles_list[0].mass = [10, 20] | units.MSun

        particles_list[1][0].position = [10, 20, 30] | units.kpc
        particles_list[1][1].position = [20, 30, 40] | units.kpc
        particles_list[1][0].velocity = [30, 40, 50] | units.kms
        particles_list[1][1].velocity = [40, 50, 60] | units.kms
        particles_list[1].mass = [100, 200] | units.MSun

        return [
            Snapshot(particles_list[0], 0 | units.Myr),
            Snapshot(particles_list[1], 1 | units.Myr),
        ]

    @patch("omtool.core.datamodel.from_fits")
    def test_run(self, from_fits_mock):
        from_fits_mock.return_value = iter(self._generate_snapshots())
        model = FITSModel("test", 1)
        actual = model.run()
        expected = self._generate_snapshots()[1]

        self.assertSnapshotsEqual(expected, actual)

    @patch("omtool.core.datamodel.from_fits")
    def test_snapshot_index_out_of_range(self, from_fits_mock):
        from_fits_mock.return_value = self._generate_snapshots()
        model = FITSModel("test", 5)
        self.assertRaises(ValueError, model.run)
