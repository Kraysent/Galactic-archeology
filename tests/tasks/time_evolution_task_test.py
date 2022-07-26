import unittest

import numpy as np
from amuse.lab import Particles, units
from amuse.units.core import IncompatibleUnitsException

from omtool.core.datamodel import Snapshot
from tasks.time_evolution_task import TimeEvolutionTask


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

        actual = task.run(self._generate_snapshot())

        self.assertTrue(
            (actual["times"] == np.array([0])).all() and (actual["values"] == np.array([1])).all()
        )

    def test_mean_function(self):
        task = TimeEvolutionTask("x", 1 | units.Myr, 1 | units.kpc, function="mean")

        actual = task.run(self._generate_snapshot())

        self.assertTrue(
            (actual["times"] == np.array([0])).all() and (actual["values"] == np.array([0.5])).all()
        )

    def test_empty_particle_set(self):
        task = TimeEvolutionTask("x", 1 | units.Myr, 1 | units.kpc, function="sum")

        snapshot = Snapshot()
        snapshot.particles.position = np.array([]) | units.kpc
        snapshot.particles.velocity = np.array([]) | units.kms
        snapshot.particles.mass = np.array([]) | units.MSun
        actual = task.run(snapshot)

        self.assertTrue(
            (actual["times"] == np.array([])).all() and (actual["values"] == np.array([])).all()
        )

    def test_expression_without_vars(self):
        task = TimeEvolutionTask("1", 1 | units.Myr, 1, function="sum")

        actual = task.run(self._generate_snapshot())

        self.assertTrue(actual["times"] == np.array([0])) and (actual["values"] == np.array([1]))

    def test_empty_expressions(self):
        self.assertRaises(RuntimeError, TimeEvolutionTask, "", 1 | units.Myr, 1, function="sum")

    def test_incompatible_units(self):
        task = TimeEvolutionTask("x + vx", 1 | units.Myr, 1 | units.kpc, function="sum")

        self.assertRaises(IncompatibleUnitsException, task.run, self._generate_snapshot())
