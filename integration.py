import time

import numpy as np
from amuse.lab import units

from archeology.integration import PyfalconIntegrator
from archeology.iotools import FITSReadManager, FITSWriteManager

manager = FITSReadManager('output/models/flat_model_in.fits')
out_manager = FITSWriteManager('output/models/flat_model_out.fits')

manager.next_frame()
snapshot = manager.read_data()
integrator = PyfalconIntegrator(snapshot, 0.2 | units.kpc, 6)

for i in range(100):
    start = time.time()
    integrator.leapfrog()

    if i % 8 == 0:
        snapshot = integrator.get_snapshot()
        out_manager.append_data(snapshot)

    print(f'{np.round(time.time() - start, 2)}\t{np.round(integrator.time, 4)}')
