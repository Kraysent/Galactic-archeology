import numpy as np

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.tasks.ellipse_fit_task import EllipseFitTask


class TestEllipseFitTask(BaseTestCase):
    def test_ideal_circle(self):
        r = 1
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        x = r * np.cos(phi)
        y = r * np.sin(phi)

        expected = {"a": 1, "e": 0}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"])
        self.assertAlmostEqual(expected["e"], actual["e"])

    def test_noisy_circle(self):
        r = np.random.random(7) * 0.000005 + 1
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        x = r * np.cos(phi)
        y = r * np.sin(phi)

        expected = {"a": 1, "e": 0}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"], 2)
        self.assertAlmostEqual(expected["e"], actual["e"], 1)

    def test_ideal_ellipse(self):
        a = 1
        b = 0.5
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        e = np.sqrt(1 - b**2 / a**2)
        x = a * np.cos(phi)
        y = b * np.sin(phi)

        expected = {"a": a, "e": e}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"])
        self.assertAlmostEqual(expected["e"], actual["e"])

    def test_noisy_ellipse(self):
        a = 1
        b = 0.5
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        e = np.sqrt(1 - b**2 / a**2)
        x = a * np.cos(phi) + np.random.random(7) * 0.000005
        y = b * np.sin(phi) + np.random.random(7) * 0.000005

        expected = {"a": a, "e": e}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"], 2)
        self.assertAlmostEqual(expected["e"], actual["e"], 1)

    def test_flat_ellipse(self):
        a = 1
        b = 0.001
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        e = np.sqrt(1 - b**2 / a**2)
        x = a * np.cos(phi) + np.random.random(7) * 0.000005
        y = b * np.sin(phi) + np.random.random(7) * 0.000005

        expected = {"a": a, "e": e}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"], 2)
        self.assertAlmostEqual(expected["e"], actual["e"], 1)

    def test_noisy_ellipse_with_offset(self):
        a = 1
        b = 0.5
        phi = np.array([0, 1, 2, 3, 4, 5, 6])
        e = np.sqrt(1 - b**2 / a**2)
        x = a * np.cos(phi) + np.random.random(7) * 0.000005 + 5
        y = b * np.sin(phi) + np.random.random(7) * 0.000005 + 7

        expected = {"a": a, "e": e}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"], 3)
        self.assertAlmostEqual(expected["e"], actual["e"], 1)

    def test_ellipse_fraction(self):
        a = 1
        b = 0.5
        phi = np.array(np.linspace(0, 0.5, 7))
        e = np.sqrt(1 - b**2 / a**2)
        x = a * np.cos(phi)
        y = b * np.sin(phi)

        expected = {"a": a, "e": e}
        actual = EllipseFitTask().run(Snapshot(), x, y)

        self.assertAlmostEqual(expected["a"], actual["a"], 2)
        self.assertAlmostEqual(expected["e"], actual["e"], 1)
