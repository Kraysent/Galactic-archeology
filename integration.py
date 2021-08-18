import time

import numpy as np
from amuse.lab import units

from archeology.integration import PyfalconIntegrator
from archeology.iotools import FITSReadManager, FITSWriteManager

manager = FITSReadManager('data/models/flat_example2.fits')
out_manager = FITSWriteManager('data/models/flat_out2.fits')

manager.next_frame()
snapshot = manager.read_data()

integrator = PyfalconIntegrator(snapshot, 0.2 | units.kpc, 8)
t = 0

print(f'CPU time\titer time\ttimestamp')
model_time = 0
i = 0

while model_time < 10000:
    model_time = integrator.timestamp.value_in(units.Myr)
    start = time.time()
    integrator.leapfrog()
    i += 1

    if i % 25 == 0:
        snapshot = integrator.get_snapshot()
        out_manager.append_data(snapshot)

    elapsed_time = time.time() - start
    t += elapsed_time

    print(f'{np.round(t, 6)}\t{np.round(elapsed_time, 6)}\t{np.round(model_time, 4)}')
