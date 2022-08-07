import unittest

import numpy as np

from omtool.core.datamodel import Snapshot


class BaseTestCase(unittest.TestCase):
    def assertNdarraysEqual(self, first: np.ndarray, second: np.ndarray):
        np.testing.assert_array_equal(first, second)

    def assertSnapshotsEqual(self, first: Snapshot, second: Snapshot):
        self.assertEqual(len(first.particles), len(second.particles))

        if len(first.particles) == 0:
            return

        self.assertNdarraysEqual(first.particles.x, second.particles.x)
        self.assertNdarraysEqual(first.particles.y, second.particles.y)
        self.assertNdarraysEqual(first.particles.z, second.particles.z)

        self.assertNdarraysEqual(first.particles.vx, second.particles.vx)
        self.assertNdarraysEqual(first.particles.vy, second.particles.vy)
        self.assertNdarraysEqual(first.particles.vz, second.particles.vz)

        self.assertNdarraysEqual(first.particles.mass, second.particles.mass)

        self.assertEqual(first.timestamp, second.timestamp)
