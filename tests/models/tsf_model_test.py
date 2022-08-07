from unittest.mock import mock_open, patch

from amuse.lab import Particles, units

from omtool.core.datamodel.snapshot import Snapshot
from omtool.core.utils import BaseTestCase
from tools.models.tsf_model import TSFModel

_test_case = """
<nemo>
    <SnapShot>
        <Parameters>
            <Nobj type="int">2</Nobj>
        </Parameters>
        <Particles>
            <Position type="float" dim="[2][3]">
                1 2 3
                4 5 6
            </Position>
            <Velocity type="float" dim="[2][3]">
                6 7 8 9 10 11
            </Velocity>
            <Mass>
                20 50
            </Mass>
        </Particles>
    </SnapShot>
</nemo>
"""


_empty_test_case = """
<nemo>
    <SnapShot>
        <Parameters>
            <Nobj type="int">0</Nobj>
        </Parameters>
        <Particles>
            <Position type="float" dim="[0][3]">
            </Position>
            <Velocity type="float" dim="[0][3]">
            </Velocity>
            <Mass>
            </Mass>
        </Particles>
    </SnapShot>
</nemo>
"""

_invalid_test_case = """
<nemo>
    <SnapShot>
        <Parameters>
            <Nobj type="int">6</Nobj>
        </Parameters>
        <Particles>
            <Position type="float" dim="[2][3]">
                1 2 3
                4 5 6
            </Position>
            <Velocity type="float" dim="[2][3]">
                6 7 8 9 10 11
            </Velocity>
            <Mass>
                20 50
            </Mass>
        </Particles>
    </SnapShot>
</nemo>
"""


class TestTSFModel(BaseTestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=_test_case)
    def test_run(self, open_mock):
        model = TSFModel("test")
        actual = model.run()

        exp_particles = Particles(2)
        exp_particles[0].position = [1, 2, 3] | units.kpc
        exp_particles[0].velocity = [6, 7, 8] | units.kms
        exp_particles[1].position = [4, 5, 6] | units.kpc
        exp_particles[1].velocity = [9, 10, 11] | units.kms
        exp_particles.mass = [20, 50] | 232500 * units.MSun

        expected = Snapshot(exp_particles)

        self.assertSnapshotsEqual(expected, actual)

    @patch("builtins.open", new_callable=mock_open, read_data=_empty_test_case)
    def test_empty_set(self, open_mock):
        model = TSFModel("test")
        actual = model.run()
        expected = Snapshot()

        self.assertSnapshotsEqual(expected, actual)

    @patch("builtins.open", new_callable=mock_open, read_data=_invalid_test_case)
    def test_bad_nobj(self, open_mock):
        model = TSFModel("test")

        self.assertRaises(AttributeError, model.run)
