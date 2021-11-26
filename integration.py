import time

import numpy as np
from amuse.lab import units

from archeology.datamodel.snapshot import Snapshot
from archeology.datamodel import Config
from archeology.integration import PyfalconIntegrator


def integrate(input_fn: str, output_fn: str):
    '''
    input_fn: str - filename of input snapshot

    output_fn: str - filename of output snapshot
    '''
    snapshot = next(Snapshot.from_fits(input_fn))

    integrator = PyfalconIntegrator(snapshot, 0.2 | units.kpc, 8)
    t = 0

    print(f'ts\tt_cpu\tt_last')
    model_time = 0
    i = 0

    while model_time < 10000:
        model_time = integrator.timestamp.value_in(units.Myr)
        start = time.time()
        integrator.leapfrog()

        if i % 15 == 0:
            snapshot = integrator.get_snapshot()
            snapshot.to_fits(output_fn, append = True)

        elapsed_time = time.time() - start
        t += elapsed_time

        print(f'{model_time:.01f}\t{t:.01f}\t{elapsed_time:.02f}')

        i += 1
