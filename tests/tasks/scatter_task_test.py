import unittest

import numpy as np
from amuse.lab import Particles, units
from amuse.units.core import IncompatibleUnitsException

from omtool.core.datamodel import Snapshot
from omtool.tasks import ScatterTask


class TestScatterTask(unittest.TestCase):
    def _generate_snapshot(self):
        particles = Particles(2)

        particles[0].position = [0, 0, 0] | units.kpc
        particles[0].velocity = [0, 0, 0] | units.kms
        particles[0].mass = 1 | units.MSun
        particles[1].position = [1, 1, 1] | units.kpc
        particles[1].velocity = [1, 1, 1] | units.kms
        particles[1].mass = 1 | units.MSun

        snapshot = Snapshot(particles)

        return snapshot

    def test_run(self):
        exprs = {"x": "x", "y": "y"}
        u = {"x": 1 | units.kpc, "y": 1 | units.kpc}
        task = ScatterTask(exprs, u, filter_barion=False)

        actual = task.run(self._generate_snapshot())

        self.assertTrue(
            (actual["x"] == np.array([0, 1])).all() and (actual["y"] == np.array([0, 1])).all()
        )

    def test_empty_particle_set(self):
        exprs = {"x": "x", "y": "y"}
        u = {"x": 1 | units.kpc, "y": 1 | units.kpc}
        task = ScatterTask(exprs, u, filter_barion=False)

        snapshot = Snapshot()
        snapshot.particles.position = np.array([]) | units.kpc
        snapshot.particles.velocity = np.array([]) | units.kms
        snapshot.particles.mass = np.array([]) | units.MSun
        actual = task.run(snapshot)

        self.assertTrue((actual["x"] == np.array([])).all() and (actual["y"] == np.array([])).all())

    def test_expressions_without_vars(self):
        exprs = {"x": "1", "y": "1"}
        u = {"x": 1, "y": 1}
        task = ScatterTask(exprs, u, False)

        actual = task.run(self._generate_snapshot())

        self.assertTrue(actual["x"] == 1) and (actual["y"] == 1)

    def test_empty_expressions(self):
        self.assertRaises(Exception, ScatterTask, {"x": "", "y": ""}, {"x": 1, "y": 1}, False)

    def test_incompatible_units(self):
        exprs = {"x": "x + vx", "y": "y"}
        u = {"x": 1 | units.kms, "y": 1 | units.kms}
        task = ScatterTask(exprs, u, False)

        self.assertRaises(IncompatibleUnitsException, task.run, self._generate_snapshot())
