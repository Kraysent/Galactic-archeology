import unittest

import numpy as np

from omtool.core.datamodel import Snapshot
from omtool.tasks import TimeEvolutionTask
from amuse.lab import Particles, units

from amuse.units.core import IncompatibleUnitsException


class TestTimeEvolutionTask(unittest.TestCase):
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

    def test_sum_function(self):
        task = TimeEvolutionTask("x", 1 | units.Myr, 1 | units.kpc, function="sum")

        t, x = task.run(self._generate_snapshot())

        self.assertTrue((x == np.array([1])).all() and (t == np.array([0])).all())

    def test_mean_function(self):
        task = TimeEvolutionTask("x", 1 | units.Myr, 1 | units.kpc, function="mean")

        t, x = task.run(self._generate_snapshot())

        self.assertTrue((x == np.array([0.5])).all() and (t == np.array([0])).all())

    def test_empty_particle_set(self):
        task = TimeEvolutionTask("x", 1 | units.Myr, 1 | units.kpc, function="sum")

        snapshot = Snapshot()
        snapshot.particles.position = np.array([]) | units.kpc
        snapshot.particles.velocity = np.array([]) | units.kms
        snapshot.particles.mass = np.array([]) | units.MSun
        t, x = task.run(snapshot)

        self.assertTrue((t == np.array([])).all() and (x == np.array([])).all())

    def test_expression_without_vars(self):
        task = TimeEvolutionTask("1", 1 | units.Myr, 1, function="sum")

        t, x = task.run(self._generate_snapshot())

        self.assertTrue(t == np.array([0])) and (x == np.array([1]))

    def test_empty_expressions(self):
        self.assertRaises(RuntimeError, TimeEvolutionTask, "", 1 | units.Myr, 1, function="sum")

    def test_incompatible_units(self):
        task = TimeEvolutionTask("x + vx", 1 | units.Myr, 1 | units.kpc, function="sum")

        self.assertRaises(IncompatibleUnitsException, task.run, self._generate_snapshot())
