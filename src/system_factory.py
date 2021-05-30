from enum import Enum

import numpy as np
from amuse.community.bhtree.interface import BHTree
from amuse.datamodel.particles import Particle, Particles
from amuse.ic.kingmodel import new_king_model
from amuse.lab import units
from amuse.units import nbody_system
from amuse.units.quantities import ScalarQuantity, VectorQuantity


def vector_from_spherical(r: ScalarQuantity, i: float, A: float):
    '''
    - r - module of vector
    - i - inclination (angle between vector and Oxy)
    - A - azimuth (angle between Oxy projection of vector and Ox)
    '''
    unit = r.unit
    r = r.value_in(unit)
    return [r * np.cos(i) * np.cos(A), r * np.cos(i) * np.sin(A), r * np.sin(i)] | unit

class Integrator(Enum):
    BHTREE = 1

class GalaxyType(Enum):
    KING = 1

class SystemFactory:
    def add_particles(self, particles: Particles):
        if not hasattr(self, 'particles'):
            self.particles = particles
        else:
            self.particles.add_particles(particles)
        
    def add_particle(self, particle: Particle):
        if not hasattr(self, 'particles'):
            self.particles = particle.as_set()
        else:
            self.particles.add_particle(particle)

    def add_system(self, system: GalaxyType, mass: ScalarQuantity, size: ScalarQuantity, N: int, r: VectorQuantity = VectorQuantity([0., 0., 0.,], units.kpc), v: VectorQuantity = VectorQuantity([0., 0., 0.,], units.kms)):
        '''
        - system - type of the system to create,
        - mass, size - its mass and size (obviously)
        - N - number of particles
        - r - initial offset of the system
        - v - initial velocity of the system
        '''
        particles = Particles()
        converter = nbody_system.nbody_to_si(mass, size)

        if system == GalaxyType.KING:
            particles = new_king_model(N, 0.6, converter)

        particles.position += r
        particles.velocity += v

        self.add_particles(particles)

    def set_integrator(self, integrator: Integrator, timestep: ScalarQuantity, epsilon_squared: ScalarQuantity):
        '''
        This probably should check if gravity was set before and use Bridge in this case
        '''
        self.particles.move_to_center()

        if integrator == Integrator.BHTREE:
            converter = nbody_system.nbody_to_si(self.particles.total_mass(), self.particles.x.max())
            self.integrator = BHTree(converter, channel_type = 'sockets')

        self.integrator.parameters.epsilon_squared = epsilon_squared
        self.integrator.parameters.timestep = timestep
        self.integrator.particles.add_particles(self.particles)

    def get_system(self):
        return self.integrator
