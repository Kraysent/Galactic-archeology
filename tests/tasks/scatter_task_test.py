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
        task = ScatterTask("x", "y", 1 | units.kpc, 1 | units.kpc, False)

        x, y = task.run(self._generate_snapshot())

        self.assertTrue((x == np.array([0, 1])).all() and (y == np.array([0, 1])).all())

    def test_empty_particle_set(self):
        task = ScatterTask("x", "y", 1 | units.kpc, 1 | units.kpc, False)

        snapshot = Snapshot()
        snapshot.particles.position = np.array([]) | units.kpc
        snapshot.particles.velocity = np.array([]) | units.kms
        snapshot.particles.mass = np.array([]) | units.MSun
        x, y = task.run(snapshot)

        self.assertTrue((x == np.array([])).all() and (y == np.array([])).all())

    def test_expressions_without_vars(self):
        task = ScatterTask("1", "1", 1, 1, False)

        x, y = task.run(self._generate_snapshot())

        self.assertTrue(x == 1) and (y == 1)

    def test_empty_expressions(self):
        self.assertRaises(RuntimeError, ScatterTask, "", "", 1, 1, False)

    def test_incompatible_units(self):
        task = ScatterTask("x + vx", "y", 1 | units.kms, 1 | units.kms, False)

        self.assertRaises(IncompatibleUnitsException, task.run, self._generate_snapshot())
