import numpy as np
from amuse.lab import Particles, VectorQuantity, units
from omtool.analysis.utils import pyfalcon_analizer


def center_of_mass(particles: Particles) -> VectorQuantity:
    return particles.center_of_mass()

def at_origin(particles: Particles) -> VectorQuantity:
    return [0, 0, 0] | units.kpc

def potential_center(particles: Particles) -> VectorQuantity:
    eps = 0.2 | units.kpc
    top_percent = 0.01

    potentials = pyfalcon_analizer.get_potentials(particles, eps)
    perm = potentials.argsort()
    positions = particles.position[perm]
    positions = positions[:int(len(positions) * top_percent)]
    masses = particles.mass[perm]
    masses = masses[:int(len(masses) * top_percent)]

    return np.sum(positions * masses[:, np.newaxis], axis = 0) / np.sum(masses)
