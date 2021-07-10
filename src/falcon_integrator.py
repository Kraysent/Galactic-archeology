from amuse.units.quantities import ScalarQuantity
from snapshot import Snapshot
import os

class FalconIntegrator:
    def __init__(self) -> None:
        pass

    def set_params(self, **kwargs):
        self.eps = kwargs['eps']
        self.kmax = kwargs['kmax']
        self.tstop = kwargs['tstop']
        self.step = kwargs['step']
        pass

    def _execute_command(self, command: str):
        os.system(command)

    def integrate(self, input_filename: str, output_filename: str):
        command = 'gyrfalcON {} {} tstop={} kmax={} eps={} step={}'.format(
            input_filename, output_filename, self.tstop, self.kmax, self.eps, self.step
        )
        self._execute_command(command)

