from amuse.lab import ScalarQuantity
from integrators.abstract_integrator import AbstractIntegrator


class NEMOhackcode1Integrator(AbstractIntegrator):
    '''
    This is only a template for class. It does nothing yet.
    '''
    def __init__(self, **kwargs):
        '''
        Essential keyword arguments:
        * nemo_path: str - path to nemo_start.sh file
        '''
        if not 'nemo_path' in kwargs:
            raise Exception('No NEMO path specified')

        self.nemo_path = kwargs['nemo_path']

    def evolve_model(self, end_time: ScalarQuantity):
        pass