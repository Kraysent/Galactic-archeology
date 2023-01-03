import unittest

import numpy as np
from amuse.lab import Particles, units
from zlog import logger

from omtool.core.datamodel import Snapshot


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        logger.formatted_streams = []

    def assertNdarraysEqual(self, first: np.ndarray, second: np.ndarray):
        np.testing.assert_array_equal(first, second)

    def assertAmuseParticlesEqual(self, first: Particles, second: Particles):
        self.assertEqual(len(first), len(second))

        if len(first) == 0:
            return

        self.assertNdarraysEqual(first.x, second.x)
        self.assertNdarraysEqual(first.y, second.y)
        self.assertNdarraysEqual(first.z, second.z)

        self.assertNdarraysEqual(first.vx, second.vx)
        self.assertNdarraysEqual(first.vy, second.vy)
        self.assertNdarraysEqual(first.vz, second.vz)

        self.assertNdarraysEqual(first.mass, second.mass)

    def assertSnapshotsEqual(self, first: Snapshot, second: Snapshot, test_kinematics: bool = True):
        self.assertEqual(len(first.particles), len(second.particles))

        self.assertEqual(first.timestamp, second.timestamp)

        if len(first.particles) == 0:
            return

        if test_kinematics:
            self.assertNdarraysEqual(first.particles.x, second.particles.x)
            self.assertNdarraysEqual(first.particles.y, second.particles.y)
            self.assertNdarraysEqual(first.particles.z, second.particles.z)

            self.assertNdarraysEqual(first.particles.vx, second.particles.vx)
            self.assertNdarraysEqual(first.particles.vy, second.particles.vy)
            self.assertNdarraysEqual(first.particles.vz, second.particles.vz)

        self.assertNdarraysEqual(first.particles.mass, second.particles.mass)

    def _generate_snapshot(self, N: int = 100) -> Snapshot:
        snapshot = Snapshot(Particles(N))
        snapshot.particles.mass = [10 * x + 1 for x in range(N)] | units.MSun
        return snapshot
