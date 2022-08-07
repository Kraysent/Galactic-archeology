import numpy as np
from amuse.lab import Particles, units
from amuse.units.core import IncompatibleUnitsException

from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase
from tools.tasks.scatter_task import ScatterTask


class TestScatterTask(BaseTestCase):
    def _generate_snapshot(self):
        particles = Particles(2)
        particles[0].position = [0, 0, 0] | units.kpc
        particles[0].velocity = [0, 0, 0] | units.kms
        particles[1].position = [1, 1, 1] | units.kpc
        particles[1].velocity = [1, 1, 1] | units.kms
        particles.mass = [1, 1] | units.MSun

        return Snapshot(particles)

    def test_run(self):
        exprs = {"x": "x", "y": "y"}
        u = {"x": 1 | units.kpc, "y": 1 | units.kpc}
        task = ScatterTask(exprs, u)

        actual = task.run(self._generate_snapshot())

        self.assertNdarraysEqual(actual["x"], np.array([0, 1]))
        self.assertNdarraysEqual(actual["y"], np.array([0, 1]))

    def test_empty_particle_set(self):
        exprs = {"x": "x", "y": "y"}
        u = {"x": 1 | units.kpc, "y": 1 | units.kpc}
        task = ScatterTask(exprs, u)

        snapshot = Snapshot()
        snapshot.particles.position = np.array([]) | units.kpc
        snapshot.particles.velocity = np.array([]) | units.kms
        snapshot.particles.mass = np.array([]) | units.MSun
        actual = task.run(snapshot)

        self.assertNdarraysEqual(actual["x"], np.array([]))
        self.assertNdarraysEqual(actual["y"], np.array([]))

    def test_expressions_without_vars(self):
        exprs = {"x": "1", "y": "1"}
        u = {"x": 1, "y": 1}
        task = ScatterTask(exprs, u)

        actual = task.run(self._generate_snapshot())

        self.assertEqual(actual["x"], 1)
        self.assertEqual(actual["y"], 1)

    def test_empty_expressions(self):
        self.assertRaises(Exception, ScatterTask, {"x": "", "y": ""}, {"x": 1, "y": 1})

    def test_incompatible_units(self):
        exprs = {"x": "x + vx", "y": "y"}
        u = {"x": 1 | units.kms, "y": 1 | units.kms}
        task = ScatterTask(exprs, u)

        self.assertRaises(IncompatibleUnitsException, task.run, self._generate_snapshot())
