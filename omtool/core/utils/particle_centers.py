import numpy as np
from amuse.lab import Particles, ScalarQuantity, VectorQuantity, units

from omtool.core.utils import pyfalcon_analizer


def center_of_mass(particles: Particles) -> VectorQuantity:
    return particles.center_of_mass()


def center_of_mass_velocity(particles: Particles) -> VectorQuantity:
    return particles.center_of_mass_velocity()


def at_origin(particles: Particles) -> VectorQuantity:
    return [0, 0, 0] | units.kpc


def at_origin_velocity(particles: Particles) -> VectorQuantity:
    return [0, 0, 0] | units.kms


def potential_center(
    particles: Particles, eps: ScalarQuantity = 0.2 | units.kpc, top_fraction: float = 0.01
) -> VectorQuantity:
    potentials = pyfalcon_analizer.get_potentials(particles, eps)
    perm = potentials.argsort()
    positions = particles.position[perm]
    positions = positions[: int(len(positions) * top_fraction)]
    masses = particles.mass[perm]
    masses = masses[: int(len(masses) * top_fraction)]

    return np.sum(positions * masses[:, np.newaxis], axis=0) / np.sum(masses)


def potential_center_velocity(
    particles: Particles, eps: ScalarQuantity = 0.2 | units.kpc, top_fraction: float = 0.01
) -> VectorQuantity:
    potentials = pyfalcon_analizer.get_potentials(particles, eps)
    perm = potentials.argsort()
    velocities = particles.velocity[perm]
    velocities = velocities[: int(len(velocities) * top_fraction)]
    masses = particles.mass[perm]
    masses = masses[: int(len(masses) * top_fraction)]

    return np.sum(velocities * masses[:, np.newaxis], axis=0) / np.sum(masses)
