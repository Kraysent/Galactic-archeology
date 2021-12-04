import logging

from amuse.lab import units

from archeology.datamodel import Config, Snapshot
from archeology.integration import PyfalconIntegrator


def integrate(config: Config):
    snapshot = next(Snapshot.from_fits(config['input_file']))

    integrator = PyfalconIntegrator(snapshot, config['eps'], config['timestep'])

    logging.info('T, Myr')
    i = 0

    if 'logs' in config.keys():
        points_to_track = { x['point_id']: x['filename'] for x in config['logs'] }
    else: 
        points_to_track = {}

    for (point_id, name) in points_to_track.items():
        with open(name, 'w') as stream:
            stream.write('T x y z vx vy vz m\n')

    while integrator.timestamp < config['model_time']:
        integrator.leapfrog()

        if i % config['snapshot_interval'] == 0:
            snapshot = integrator.get_snapshot()
            snapshot.to_fits(config['output_file'], append = True)

        for (point_id, name) in points_to_track.items():
            with open(name, 'a') as stream:
                particle = integrator.get_particle(point_id)
                x, y, z = particle.position.value_in(units.kpc)
                vx, vy, vz = particle.velocity.value_in(units.kms)
                m = particle.mass.value_in(units.MSun)
                T = integrator.timestamp.value_in(units.Myr)
                stream.write(f'{T} {x} {y} {z} {vx} {vy} {vz} {m}\n')

        logging.info(f'{integrator.timestamp.value_in(units.Myr):.01f}')

        i += 1
