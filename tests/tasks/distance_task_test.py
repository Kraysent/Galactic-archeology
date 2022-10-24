import numpy as np
from amuse.lab import units

from omtool.core.utils import BaseTestCase
from tools.tasks.distance_task import DistanceTask


class TestDistanceTask(BaseTestCase):
    def test_single_iteration(self):
        task = DistanceTask()

        snapshot = self._generate_snapshot()
        snapshot.timestamp = 0 | units.Myr
        actual = task.run(snapshot, start=[0, 0, 0] | units.kpc, end=[1, 0, 0] | units.kpc)
        expected = {"times": np.array([0]), "dist": np.array([1])}

        self.assertEqual(len(actual), len(expected))

        for key in expected:
            self.assertNdarraysEqual(actual[key], expected[key])

    def test_three_iterations(self):
        task = DistanceTask()

        snapshot = self._generate_snapshot()
        snapshot.timestamp = 0 | units.Myr
        task.run(snapshot, start=[0, 0, 0] | units.kpc, end=[1, 0, 0] | units.kpc)
        snapshot.timestamp = 10 | units.Myr
        task.run(snapshot, start=[0, 0, 0] | units.kpc, end=[2, 0, 0] | units.kpc)
        snapshot.timestamp = 20 | units.Myr
        actual = task.run(snapshot, start=[0, 0, 0] | units.kpc, end=[3, 0, 0] | units.kpc)
        expected = {"times": np.array([0, 10, 20]), "dist": np.array([1, 2, 3])}

        self.assertEqual(len(actual), len(expected))

        for key in expected:
            self.assertNdarraysEqual(actual[key], expected[key])
