import logging

from amuse.lab import units

from archeology.datamodel import Config, Snapshot
from archeology.integration import PyfalconIntegrator


def integrate(config: Config):
    snapshot = next(Snapshot.from_fits(config['input_file']))

    integrator = PyfalconIntegrator(snapshot, config['eps'], config['timestep'])
    t = 0

    logging.info('T, Myr')
    i = 0

    while integrator.timestamp < config['model_time']:
        integrator.leapfrog()

        if i % config['snapshot_interval'] == 0:
            snapshot = integrator.get_snapshot()
            snapshot.to_fits(config['output_file'], append = True)

        logging.info(f'{integrator.timestamp.value_in(units.Myr):.01f}')

        i += 1
