from amuse.datamodel.particles import Particles
from amuse.units import nbody_system
from integrators.abstract_integrator import AbstractIntegrator
from amuse.community.bhtree.interface import BHTree
from amuse.lab import ScalarQuantity


class BHTreeAMUSEIntegrator(AbstractIntegrator):
    def __init__(self, **kwargs):
        '''
        Essential keyword arguments:
        * mass: ScalarQuantity - total mass of the system
        * rscale: ScalarQuantity - length scale of the system (usually virial radius)

        Not essential keyword arguments:
        * timestep - timestep provided to integrator
        * epsilon_squared - epsilon provided to integrator
        '''
        if not 'mass' in kwargs:
            raise Exception('No mass provided to BHTree integrator')

        if not 'rscale' in kwargs:
            raise Exception('No rscale provided to BHTree integrator')

        converter = nbody_system.nbody_to_si(kwargs['mass'], kwargs['rscale'])
        kwargs.pop('mass')
        kwargs.pop('rscale')

        self._integrator = BHTree(converter, channel_type = 'sockets')

        for (key, value) in kwargs.items():
            if hasattr(self._integrator.parameters, key):
                setattr(self._integrator.parameters, key, value)

    def evolve_model(self, time: ScalarQuantity):
        self._integrator.evolve_model(time)
        self._raise_subscribers()

    @property
    def model_time(self):
        return self._integrator.model_time

    @property
    def particles(self) -> Particles:
        return self._integrator.particles

    @particles.setter
    def particles(self, value: Particles):
        self._integrator.setup_particles(value)

    @property
    def timestep(self):
        return self._integrator.parameters.timestep

    @timestep.setter
    def timestep(self, value: ScalarQuantity):
        self._integrator.parameters.timestep = value

    
