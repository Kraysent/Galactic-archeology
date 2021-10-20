import time

import numpy as np
from amuse.lab import units

from archeology.datamodel.snapshot import Snapshot
from archeology.integration import PyfalconIntegrator


def integrate(datadir: str):
    snapshot = next(Snapshot.from_fits(f'{datadir}/models/bh_100x_flat_without_galaxy.fits'))

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
            snapshot.to_fits(f'{datadir}/models/bh_100x_flat_wgalaxy_out.fits', append = True)

        elapsed_time = time.time() - start
        t += elapsed_time

        print(f'{model_time:.01f}\t{t:.01f}\t{elapsed_time:.02f}')

        i += 1
