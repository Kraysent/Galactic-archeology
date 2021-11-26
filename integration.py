import time

from amuse.lab import units

from archeology.datamodel import Config, Snapshot
from archeology.integration import PyfalconIntegrator


def integrate(config: Config):
    snapshot = next(Snapshot.from_fits(config.input_file))

    integrator = PyfalconIntegrator(snapshot, config.eps, config.timestep)
    t = 0

    print(f'ts\tt_cpu\tt_last')
    i = 0

    while integrator.timestamp < config.model_time:
        start = time.time()
        integrator.leapfrog()

        if i % config.snapshot_interval == 0:
            snapshot = integrator.get_snapshot()
            snapshot.to_fits(config.output_file, append = True)

        elapsed_time = time.time() - start
        t += elapsed_time

        print(f'{integrator.timestamp.value_in(units.Myr):.01f}\t{t:.01f}\t{elapsed_time:.02f}')

        i += 1
