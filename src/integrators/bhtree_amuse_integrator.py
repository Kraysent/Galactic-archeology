from logging import setLogRecordFactory
from amuse.units import nbody_system
from integrators.abstract_integrator import AbstractIntegrator
from amuse.community.bhtree.interface import BHTree
from amuse.lab import ScalarQuantity


class BHTreeAMUSEIntegrator(AbstractIntegrator):
    def __init__(self, **kwargs):
        if not 'mass' in kwargs:
            raise Exception('No mass provided to BHTree integrator')

        if not 'rscale' in kwargs:
            raise Exception('No rscale provided to BHTree integrator')

        converter = nbody_system.nbody_to_si(kwargs['mass'], kwargs['rscale'])

        self._integrator = BHTree(converter, channel_type = 'sockets')

        for (key, value) in kwargs:
            if hasattr(self._integrator.parameters, key):
                setattr(self._integrator.parameters, value)

    def evolve_model(self, time: ScalarQuantity):
        self._integrator.evolve_model(time)

    @property
    def model_time(self):
        return self._integrator.model_time

    @property
    def timestep(self):
        return self._integrator.parameters.timestep

    @timestep.setter
    def timestep(self, value):
        self._integrator.parameters.timestep = value

